import requests
import json
from pprint import pprint


def get_preconfs(
    page=1, limit=50, bidder=None, block_number_min=None, block_number_max=None
):
    """
    Fetch data from the /preconfs endpoint.
    """
    url = "http://localhost:8000/preconfs"
    params = {"page": page, "limit": limit}

    # Add optional parameters if provided
    if bidder:
        params["bidder"] = bidder
    if block_number_min is not None:
        params["block_number_min"] = block_number_min
    if block_number_max is not None:
        params["block_number_max"] = block_number_max

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching /preconfs: {http_err}")
    except Exception as err:
        print(f"An error occurred while fetching /preconfs: {err}")
    return None


def get_preconfs_aggregations(group_by_field):
    """
    Fetch data from the /preconfs/aggregations endpoint.
    """
    url = "http://localhost:8000/preconfs/aggregations"
    params = {"group_by_field": group_by_field}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching /preconfs/aggregations: {http_err}")
    except Exception as err:
        print(f"An error occurred while fetching /preconfs/aggregations: {err}")
    return None


def main():
    # Fetch Preconfs Data
    print("Fetching Preconfs Data...\n")
    preconfs_data = get_preconfs(
        page=1,
        limit=10,  # Adjust as needed
        bidder=None,  # Replace with a bidder name if filtering is desired
        block_number_min=1000,  # Replace with desired minimum block number
        block_number_max=5000,  # Replace with desired maximum block number
    )

    if preconfs_data:
        print("Preconfs Data:")
        pprint(preconfs_data, indent=2)
    else:
        print("Failed to retrieve Preconfs data.")

    print("\n" + "=" * 50 + "\n")

    # Fetch Preconfs Aggregations Data
    print("Fetching Preconfs Aggregations Data...\n")
    aggregations_data = get_preconfs_aggregations(group_by_field="bidder")

    if aggregations_data:
        print("Preconfs Aggregations Data:")
        pprint(aggregations_data, indent=2)
    else:
        print("Failed to retrieve Preconfs Aggregations data.")


if __name__ == "__main__":
    main()
