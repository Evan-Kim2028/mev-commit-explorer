# models.py

from pydantic import BaseModel
from typing import List, Optional, Union


class PreconfDataItem(BaseModel):
    commitmentIndex: int
    committer: str
    commitmentDigest: str
    bidder: str
    isSlash: bool
    commitmentSignature: str
    bid: int
    inc_block_number: int
    bidHash: str
    decayStartTimeStamp: int
    decayEndTimeStamp: int
    txnHash: str
    revertingTxHashes: Optional[str]
    bidSignature: str
    sharedSecretKey: str
    block_number: int
    block_number_l1: int
    extra_data_l1: Optional[str]
    to_l1: str
    from_l1: str
    nonce_l1: int
    type_l1: int
    block_hash_l1: str
    timestamp_l1: int
    base_fee_per_gas_l1: int
    gas_used_block_l1: int
    parent_beacon_block_root: str
    max_priority_fee_per_gas_l1: int
    max_fee_per_gas_l1: int
    effective_gas_price_l1: int
    gas_used_l1: int


class PreconfsResponse(BaseModel):
    page: int
    limit: int
    total: int
    data: List[PreconfDataItem]


class AggregationResult(BaseModel):
    preconf_count: int
    average_bid: float
    total_bid: float
    group_by_value: Union[
        str, int
    ]  # Adjust the type based on possible group_by_field types


class TableSchemaItem(BaseModel):
    column_name: str
    data_type: str
