import pytest
from api.main import PreconfDataItem
from pydantic import ValidationError


def test_preconf_data_item_valid():
    valid_data = {
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
    }
    item = PreconfDataItem(**valid_data)
    assert item.commitmentIndex == 1
    assert item.isSlash is False


def test_preconf_data_item_invalid():
    invalid_data = {
        "commitmentIndex": "should be int",
        # Missing required fields...
    }
    with pytest.raises(ValidationError) as exc_info:
        PreconfDataItem(**invalid_data)
    errors = exc_info.value.errors()
    assert len(errors) > 0
