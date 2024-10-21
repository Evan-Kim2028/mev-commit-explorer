import polars as pl
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from api.models import PreconfsResponse, AggregationResult, TableSchemaItem

from api.database import (
    get_commitments,
    get_db_connection,
    load_commitments_df,
    get_table_schema,
)

app = FastAPI(title="DuckDB Table Row Counts API")

# Enable CORS for the frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the frontend's origin for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tables", response_model=List[str])
def list_tables():
    """
    List all available tables in the DuckDB database.

    Returns:
        List[str]: A list of table names available in the DuckDB.

    Raises:
        HTTPException: If there is an error querying the database, returns a 500 status code.
    """
    try:
        with get_db_connection() as conn:
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
        return table_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/preconfs", response_model=PreconfsResponse)
def get_preconfs(
    page: int = Query(1, ge=1, description="Page number for pagination (default: 1)."),
    limit: int = Query(
        50, ge=1, le=100, description="Limit of items per page (default: 50)."
    ),
    bidder: Optional[str] = Query(None, description="Filter by bidder address."),
    block_number_min: Optional[int] = Query(
        None, description="Minimum block number to filter by."
    ),
    block_number_max: Optional[int] = Query(
        None, description="Maximum block number to filter by."
    ),
):
    """
    Get preconfs data with optional filters, paginated.

    Args:
        page (int): Page number for pagination (default: 1).
        limit (int): Number of rows per page (default: 50, maximum: 100).
        bidder (Optional[str]): Optional filter for bidder address.
        block_number_min (Optional[int]): Optional filter for minimum block number.
        block_number_max (Optional[int]): Optional filter for maximum block number.

    Returns:
        dict: Paginated results with 'page', 'limit', 'total' rows, and the filtered data.

    Raises:
        HTTPException: If there is an error retrieving data, returns a 500 status code.
    """
    try:
        commitments_df = get_commitments(
            bidder=bidder,
            block_number_min=block_number_min,
            block_number_max=block_number_max,
        )

        total_rows = commitments_df.height
        offset = (page - 1) * limit

        paginated_df = commitments_df.sort("inc_block_number", descending=True).slice(
            offset, limit
        )

        result = paginated_df.to_dicts()

        return {"page": page, "limit": limit, "total": total_rows, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/preconfs/aggregations", response_model=List[AggregationResult])
def get_preconfs_aggregations(
    group_by_field: str = Query(
        ..., description="Field to group by (e.g., 'bidder' or 'inc_block_number')."
    ),
):
    """
    Get group-by aggregations on preconfs data.

    Args:
        group_by_field (str): Field to group the preconfs data by.

    Returns:
        List[Dict[str, Any]]: Aggregated results with counts and bid-related calculations.

    Raises:
        HTTPException: If there is an error performing the aggregation, returns a 500 status code.
    """
    try:
        df = load_commitments_df()

        agg_df = df.group_by(group_by_field).agg(
            [
                pl.count().alias("preconf_count"),
                (pl.mean("bid") / 10**18).alias("average_bid"),
                (pl.sum("bid") / 10**18).alias("total_bid"),
            ]
        )

        result = agg_df.to_dicts()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tables/{table_name}/schema", response_model=List[TableSchemaItem])
def get_table_schema_endpoint(table_name: str):
    """
    Retrieve the schema of a specified DuckDB table.

    Args:
        table_name (str): Name of the table to retrieve the schema from.

    Returns:
        List[Dict[str, str]]: A list of column names and their data types for the specified table.

    Raises:
        HTTPException: If there is an error retrieving the table schema, returns a 500 status code.
    """
    try:
        schema = get_table_schema(table_name)
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
