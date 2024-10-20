# database.py

import os
import duckdb
import polars as pl
import logging
from typing import Optional
from db_lock import acquire_lock, release_lock  # Import the locking functions
from fastapi import HTTPException  # Only import HTTPException for error handling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database filename from the environment variable
DB_FILENAME = os.getenv("DATABASE_URL", "/app/db_data/mev_commit.duckdb")


def get_db_connection():
    """Establishes and returns a DuckDB connection."""
    try:
        return duckdb.connect(DB_FILENAME, read_only=True)
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


def load_commitments_df() -> pl.DataFrame:
    """
    Load and process the commitments DataFrame.
    """
    # Acquire lock before accessing DuckDB
    lockfile = acquire_lock()
    try:
        conn = get_db_connection()

        # Read the tables
        encrypted_stores_df = conn.execute("SELECT * FROM encrypted_stores").pl()
        commit_stores_df = conn.execute("SELECT * FROM commit_stores").pl()
        commits_processed_df = conn.execute("SELECT * FROM commits_processed").pl()
        l1_txs = conn.execute("SELECT * FROM l1_transactions").pl()

        conn.close()

        # Perform joins
        commitments_df = (
            encrypted_stores_df.select(
                "commitmentIndex", "committer", "commitmentDigest"
            )
            .join(
                commit_stores_df,
                on="commitmentIndex",
                how="inner",
                suffix="_opened_commit",
            )
            .with_columns((pl.lit("0x") + pl.col("txnHash")).alias("txnHash"))
            .join(
                commits_processed_df.select("commitmentIndex", "isSlash"),
                on="commitmentIndex",
                how="inner",
            )
            .join(
                l1_txs,
                left_on="txnHash",
                right_on="hash",
                suffix="_l1",
            )
            .rename(
                {"blockNumber": "inc_block_number"}  # desired block number for preconf
            )
        )

        # Select desired columns
        commitments_df = commitments_df.select(
            "commitmentIndex",
            "committer",
            "commitmentDigest",
            "bidder",
            "isSlash",
            "commitmentSignature",
            "bid",
            "inc_block_number",
            "bidHash",
            "decayStartTimeStamp",
            "decayEndTimeStamp",
            "txnHash",
            "revertingTxHashes",
            "bidSignature",
            "sharedSecretKey",
            "block_number",  # mev-commit block number
            # the l1 transaction data
            "block_number_l1",
            "extra_data_l1",
            "to_l1",
            "from_l1",
            "nonce_l1",
            "type_l1",
            "block_hash_l1",
            "timestamp_l1",
            "base_fee_per_gas_l1",
            "gas_used_block_l1",
            "parent_beacon_block_root",
            "max_priority_fee_per_gas_l1",
            "max_fee_per_gas_l1",
            "effective_gas_price_l1",
            "gas_used_l1",
        )

        return commitments_df
    except Exception as e:
        logger.error(f"Error loading commitments data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        # Release the lock after operation is done
        release_lock(lockfile)


def get_commitments(
    bidder: Optional[str] = None,
    block_number_min: Optional[int] = None,
    block_number_max: Optional[int] = None,
) -> pl.DataFrame:
    """
    Retrieve commitments with optional filtering.
    """
    try:
        df = load_commitments_df()

        # Apply filters if any
        if bidder:
            df = df.filter(pl.col("bidder") == bidder)

        if block_number_min is not None:
            df = df.filter(pl.col("inc_block_number") >= block_number_min)

        if block_number_max is not None:
            df = df.filter(pl.col("inc_block_number") <= block_number_max)

        return df
    except Exception as e:
        logger.error(f"Error retrieving commitments: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
