import asyncio
import os
import polars as pl
import time
import logging
from typing import Dict, Union, Optional
from hypermanager.events import EventConfig
from hypermanager.manager import HyperManager
from hypermanager.protocols.mev_commit import mev_commit_config
from data_processing import (
    get_latest_block_number,
    write_to_duckdb,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Define your event configurations globally
opened_commits_config = EventConfig(
    name=mev_commit_config["OpenedCommitmentStored"].name,
    signature=mev_commit_config["OpenedCommitmentStored"].signature,
    column_mapping=mev_commit_config["OpenedCommitmentStored"].column_mapping,
)

unopened_commits_config = EventConfig(
    name=mev_commit_config["UnopenedCommitmentStored"].name,
    signature=mev_commit_config["UnopenedCommitmentStored"].signature,
    column_mapping=mev_commit_config["UnopenedCommitmentStored"].column_mapping,
)

commits_processed_config = EventConfig(
    name=mev_commit_config["CommitmentProcessed"].name,
    signature=mev_commit_config["CommitmentProcessed"].signature,
    column_mapping=mev_commit_config["CommitmentProcessed"].column_mapping,
)


async def fetch_l1_txs(l1_tx_list: Union[str, list[str]]) -> Optional[pl.DataFrame]:
    """
    Fetch L1 transaction data from the hypersync client in chunks of 3000.
    Returns a concatenated DataFrame or None if no data is fetched.
    """
    if not l1_tx_list:
        logger.info("No L1 transaction hashes to query.")
        return None

    if isinstance(l1_tx_list, str):
        l1_tx_list = [l1_tx_list]

    manager = HyperManager(url="https://holesky.hypersync.xyz")
    dataframes = []

    def chunked(iterable, n):
        """Yield successive n-sized chunks from the iterable."""
        for i in range(0, len(iterable), n):
            yield iterable[i : i + n]

    for chunk in chunked(l1_tx_list, 3000):
        try:
            l1_txs_chunk = await asyncio.wait_for(manager.search_txs(txs=chunk), 30)
            if l1_txs_chunk is not None and not l1_txs_chunk.is_empty():
                dataframes.append(l1_txs_chunk)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout while fetching L1 transactions for chunk: {e}")
            continue
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching L1 transactions for chunk: {e}"
            )
            continue

    if not dataframes:
        logger.info("No L1 transactions found.")
        return None

    l1_txs_df = pl.concat(dataframes)
    return l1_txs_df


async def get_events():
    """
    Fetch event logs from the MEV-Commit system and store them in DuckDB tables.
    Then load the data from DuckDB, perform joins, and return the commitments DataFrame.
    """
    manager = HyperManager(url="https://mev-commit.hypersync.xyz")

    db_dir = "db/data"
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logging.info(f"Created directory: {db_dir}")

    db_filename = os.path.join(db_dir, "mev_commit.duckdb")

    # Get the latest block numbers from each table
    latest_blocks = {}

    # List of tables with their event configurations and block number column names
    tables = [
        {
            "table_name": "commit_stores",
            "block_column": "block_number",
            "event_config": opened_commits_config,
        },
        {
            "table_name": "encrypted_stores",
            "block_column": "block_number",
            "event_config": unopened_commits_config,
        },
        {
            "table_name": "commits_processed",
            "block_column": "block_number",
            "event_config": commits_processed_config,
        },
    ]

    # Get the latest block numbers and aggregate logs
    latest_blocks_info = []
    for table in tables:
        latest_block = get_latest_block_number(
            table["table_name"], table["block_column"], db_filename
        )
        latest_blocks[table["table_name"]] = latest_block
        latest_blocks_info.append(f"{table['table_name']}: {latest_block}")
    logging.info("Latest blocks - " + "; ".join(latest_blocks_info))

    # Query events and get Polars DataFrames
    fetched_records_info = []
    dataframes: Dict[str, pl.DataFrame] = {}

    for table in tables:
        table_name = table["table_name"]
        event_config = table["event_config"]
        from_block = latest_blocks.get(table_name, 0) + 1

        try:
            df: pl.DataFrame = await manager.execute_event_query(
                event_config,
                tx_data=True,
                from_block=from_block,
            )
            record_count = len(df)
            dataframes[table_name] = df
            fetched_records_info.append(f"{table_name}: {record_count} new records")

            # For 'commit_stores', fetch l1_transactions and store them in a separate table
            if table_name == "commit_stores" and not df.is_empty():
                l1_txs_list = (
                    df.with_columns((pl.lit("0x") + pl.col("txnHash")).alias("txnHash"))
                    .select("txnHash")
                    .unique()["txnHash"]
                    .to_list()
                )

                l1_txs_df = await fetch_l1_txs(l1_txs_list)
                if l1_txs_df is not None and not l1_txs_df.is_empty():
                    # Store l1_txs_df in dataframes with key 'l1_transactions'
                    dataframes["l1_transactions"] = l1_txs_df
                    l1_record_count = len(l1_txs_df)
                    fetched_records_info.append(
                        f"l1_transactions: {l1_record_count} new records"
                    )
                else:
                    fetched_records_info.append("l1_transactions: 0 new records")

        except ValueError as e:
            dataframes[table_name] = pl.DataFrame()  # Empty DataFrame
            fetched_records_info.append(f"{table_name}: 0 new records")

    logging.info("Fetched records - " + "; ".join(fetched_records_info))

    # Write each DataFrame to its own DuckDB table
    write_info = []
    for table_name, df in dataframes.items():
        # Added error handling to skip None or empty DataFrames
        if df is None or df.is_empty():
            write_info.append(f"{table_name}: No new data to write.")
            continue
        write_result = write_to_duckdb(df, table_name, db_filename)
        write_info.append(write_result)
    logging.info("Write to DuckDB - " + "; ".join(write_info))


if __name__ == "__main__":
    # Run the async function in a loop every 30 seconds
    while True:
        asyncio.run(get_events())
        time.sleep(30)  # Wait for 30 seconds before fetching new data
