import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import (
    app,
    PreconfDataItem,
    PreconfsResponse,
    AggregationResult,
    TableSchemaItem,
)
import polars as pl

# Since we have a test_client fixture in conftest.py, we can use it here
# The fixture provides a TestClient instance to make requests to the FastAPI app


def mock_get_commitments(*args, **kwargs):
    """
    Mock function for get_commitments.
    Returns a Polars DataFrame with predefined data.
    """
    mock_data = [
        {
            "commitmentIndex": 1,
            "committer": "0x123...",
            "commitmentDigest": "0xabc...",
            "bidder": "0x456...",
            "isSlash": False,
            "commitmentSignature": "0xdef...",
            "bid": 1000000000000000000,
            "inc_block_number": 123456,
            "bidHash": "0x789...",
            "decayStartTimeStamp": 1620000000,
            "decayEndTimeStamp": 1620003600,
            "txnHash": "0xghi...",
            "revertingTxHashes": None,
            "bidSignature": "0xjkl...",
            "sharedSecretKey": "0xmnop...",
            "block_number": 654321,
            "block_number_l1": 654322,
            "extra_data_l1": None,
            "to_l1": "0xaaa...",
            "from_l1": "0xbbb...",
            "nonce_l1": 0,
            "type_l1": 2,
            "block_hash_l1": "0xccc...",
            "timestamp_l1": 1620000000,
            "base_fee_per_gas_l1": 1000000000,
            "gas_used_block_l1": 21000,
            "parent_beacon_block_root": "0xddd...",
            "max_priority_fee_per_gas_l1": 2000000000,
            "max_fee_per_gas_l1": 3000000000,
            "effective_gas_price_l1": 2500000000,
            "gas_used_l1": 21000,
        },
        # You can add more mock items as needed
    ]
    return pl.DataFrame(mock_data)


def mock_load_commitments_df(*args, **kwargs):
    """
    Mock function for load_commitments_df.
    Returns a Polars DataFrame with predefined data for aggregations.
    """
    mock_data = [
        {"bidder": "0x456...", "bid": 1000000000000000000, "inc_block_number": 123456},
        {"bidder": "0x456...", "bid": 2000000000000000000, "inc_block_number": 123457},
        {"bidder": "0x789...", "bid": 1500000000000000000, "inc_block_number": 123458},
    ]
    return pl.DataFrame(mock_data)


def mock_get_table_schema(table_name: str):
    """
    Mock function for get_table_schema.
    Returns a list of dictionaries representing the schema of the table.
    """
    mock_schema = [
        {"column_name": "id", "data_type": "INTEGER"},
        {"column_name": "name", "data_type": "VARCHAR"},
        {"column_name": "created_at", "data_type": "TIMESTAMP"},
    ]
    return mock_schema


@pytest.mark.parametrize(
    "endpoint, method, expected_status",
    [
        ("/tables", "get", 200),
        ("/preconfs", "get", 200),
        ("/preconfs/aggregations?group_by_field=bidder", "get", 200),
        ("/tables/sample_table/schema", "get", 200),
    ],
)
def test_endpoints_success(test_client: TestClient, endpoint, method, expected_status):
    """
    Generic test to check successful responses for various endpoints.
    """
    with patch("api.database.get_commitments", side_effect=mock_get_commitments), patch(
        "api.database.load_commitments_df", side_effect=mock_load_commitments_df
    ), patch("api.database.get_table_schema", side_effect=mock_get_table_schema):
        if method == "get":
            response = test_client.get(endpoint)
        else:
            response = test_client.post(endpoint)  # Extend as needed

        assert response.status_code == expected_status

        if endpoint.startswith("/tables") and endpoint.endswith("/schema"):
            # Test for /tables/{table_name}/schema
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            for item in data:
                assert "column_name" in item
                assert "data_type" in item
        elif endpoint == "/tables":
            # Test for /tables
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert all(isinstance(table, str) for table in data)
        elif endpoint.startswith("/preconfs/aggregations"):
            # Test for /preconfs/aggregations
            data = response.json()
            assert isinstance(data, list)
            for item in data:
                assert "group_by_value" in item
                assert "preconf_count" in item
                assert "average_bid" in item
                assert "total_bid" in item
        elif endpoint == "/preconfs":
            # Test for /preconfs
            data = response.json()
            assert "page" in data
            assert "limit" in data
            assert "total" in data
            assert "data" in data
            assert isinstance(data["data"], list)
            for item in data["data"]:
                # Validate using Pydantic model
                PreconfDataItem(**item)


@pytest.mark.parametrize(
    "endpoint, method, expected_status",
    [
        ("/preconfs?limit=150", "get", 422),  # Exceeding limit
        ("/preconfs?page=0", "get", 422),  # Invalid page number
        (
            "/preconfs/aggregations?group_by_field=invalid_field",
            "get",
            500,
        ),  # Invalid group_by_field
    ],
)
def test_endpoints_validation_errors(
    test_client: TestClient, endpoint, method, expected_status
):
    """
    Test endpoints with invalid parameters to ensure proper error handling.
    """
    with patch("api.database.get_commitments", side_effect=mock_get_commitments), patch(
        "api.database.load_commitments_df", side_effect=mock_load_commitments_df
    ), patch("api.database.get_table_schema", side_effect=mock_get_table_schema):
        if method == "get":
            response = test_client.get(endpoint)
        else:
            response = test_client.post(endpoint)  # Extend as needed

        assert response.status_code == expected_status
        data = response.json()
        assert "detail" in data


def test_list_tables_success(test_client: TestClient):
    """
    Test the /tables endpoint for successful response.
    """
    with patch("api.database.get_db_connection") as mock_db_conn:
        # Mock the execute and fetchall methods
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("table1",), ("table2",)]
        mock_db_conn.return_value.__enter__.return_value = mock_cursor

        response = test_client.get("/tables")
        assert response.status_code == 200
        data = response.json()
        assert data == ["table1", "table2"]


def test_get_table_schema_success(test_client: TestClient):
    """
    Test the /tables/{table_name}/schema endpoint for successful response.
    """
    with patch("api.database.get_table_schema", side_effect=mock_get_table_schema):
        response = test_client.get("/tables/sample_table/schema")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["column_name"] == "id"
        assert data[0]["data_type"] == "INTEGER"


def test_get_table_schema_not_found(test_client: TestClient):
    """
    Test the /tables/{table_name}/schema endpoint when the table does not exist.
    """
    with patch("api.database.get_table_schema") as mock_get_table_schema:
        mock_get_table_schema.side_effect = Exception(
            "Table 'nonexistent_table' not found."
        )
        response = test_client.get("/tables/nonexistent_table/schema")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Table 'nonexistent_table' not found."


def test_get_preconfs_success(test_client: TestClient):
    """
    Test the /preconfs endpoint for successful response.
    """
    with patch("api.database.get_commitments", side_effect=mock_get_commitments):
        response = test_client.get("/preconfs?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10
        assert data["total"] == 1  # Based on mock_get_commitments
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        # Validate using Pydantic model
        PreconfDataItem(**data["data"][0])


def test_get_preconfs_aggregations_success(test_client: TestClient):
    """
    Test the /preconfs/aggregations endpoint for successful response.
    """
    with patch(
        "api.database.load_commitments_df", side_effect=mock_load_commitments_df
    ):
        response = test_client.get("/preconfs/aggregations?group_by_field=bidder")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # Based on mock_load_commitments_df
        for item in data:
            AggregationResult(**item)


def test_get_preconfs_aggregations_invalid_group_by(test_client: TestClient):
    """
    Test the /preconfs/aggregations endpoint with an invalid group_by_field.
    """
    with patch(
        "api.database.load_commitments_df", side_effect=mock_load_commitments_df
    ):
        response = test_client.get(
            "/preconfs/aggregations?group_by_field=invalid_field"
        )
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


def test_get_preconfs_with_filters(test_client: TestClient):
    """
    Test the /preconfs endpoint with filters applied.
    """
    with patch("api.database.get_commitments", side_effect=mock_get_commitments):
        response = test_client.get("/preconfs?bidder=0x456...")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["data"]) == 1
        assert data["data"][0]["bidder"] == "0x456..."


def test_get_preconfs_invalid_limit(test_client: TestClient):
    """
    Test the /preconfs endpoint with a limit exceeding the maximum allowed.
    """
    response = test_client.get("/preconfs?limit=150")
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data


def test_get_preconfs_invalid_page(test_client: TestClient):
    """
    Test the /preconfs endpoint with an invalid page number.
    """
    response = test_client.get("/preconfs?page=0")
    assert response.status_code == 422  # Unprocessable Entity
    data = response.json()
    assert "detail" in data
