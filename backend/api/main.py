import polars as pl
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from api.database import get_commitments, get_db_connection, load_commitments_df

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
    List all available tables in the database.
    """
    try:
        with get_db_connection() as conn:
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
        return table_names
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/preconfs")
def get_preconfs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    bidder: Optional[str] = Query(None),
    block_number_min: Optional[int] = Query(None),
    block_number_max: Optional[int] = Query(None),
):
    """
    Get preconfs data with optional filters, paginated.
    """
    try:
        # Retrieve filtered DataFrame
        commitments_df = get_commitments(
            bidder=bidder,
            block_number_min=block_number_min,
            block_number_max=block_number_max,
        )

        # Implement pagination: order by 'inc_block_number' descending to get the latest rows
        total_rows = commitments_df.height
        offset = (page - 1) * limit

        # Get the paginated data
        paginated_df = commitments_df.sort("inc_block_number", descending=True).slice(
            offset, limit
        )

        # Convert to list of dictionaries
        result = paginated_df.to_dicts()

        return {"page": page, "limit": limit, "total": total_rows, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/preconfs/aggregations")
def get_preconfs_aggregations(
    group_by_field: str = Query(..., description="Field to group by"),
):
    """
    Get groupby aggregations on preconfs data.
    """
    try:
        # Load the DataFrame
        df = load_commitments_df()

        # Perform groupby aggregation
        agg_df = df.group_by(group_by_field).agg(
            [
                pl.count().alias("preconf_count"),
                (pl.mean("bid") / 10**18).alias("average_bid"),
                (pl.sum("bid") / 10**18).alias("total_bid"),
            ]
        )

        # Convert to list of dictionaries
        result = agg_df.to_dicts()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
