from copy import deepcopy
import pytest
from eth.constants import (
    ZERO_HASH32,
    EMPTY_UNCLE_HASH,
)
from eth.chains.base import MiningChain, Chain
from eth.vm.forks import BerlinVM
from eth.vm.forks.berlin.transactions import (
    BerlinTransactionBuilder,
)
import eth.tools.builder.chain as builder
from eth.rlp.headers import BlockHeader
from eth_bloom import BloomFilter

import eth2spec.merge.spec as spec

from eth1 import (
    Eth1Rpc,
    MergedConsensus,
)
from beacon_helpers import (
    _verify_execution_state_transition,
)


@pytest.fixture
def eth1_rpc():
    # Hack BerlinVM
    # BerlinVM.consensus_class = MergedConsensus
    Eth1Chain = builder.build(
        MiningChain,
        builder.fork_at(BerlinVM, 0),
        builder.disable_pow_check(),
    )
    # Eth1Chain = builder.enable_pow_mining(Eth1Chain)
    eth1_rpc = Eth1Rpc(Eth1Chain)
    return eth1_rpc


def test_verify_execution_state_transition(eth1_rpc):
    # TODO: test transactions
    # transaction = BerlinTransactionBuilder.create_unsigned_transaction(cls,
    #     *,
    #     nonce: int,
    #     gas_price: int,
    #     gas: int,
    #     to: Address,
    #     value: int,
    #     data: bytes
    # )

    head_block = eth1_rpc.get_head_block()
    assert head_block.header.block_number == 0

    # Build block with a separate instance
    new_eth1_rpc = deepcopy(eth1_rpc)
    parent_hash = head_block.header.hash
    new_block = new_eth1_rpc.consensus_assembleBlock(
        extra_data=b'fork', parent_hash=parent_hash)

    new_block = new_block.copy(
        header=new_block.header.copy(
            bloom=0,  # TODO
            difficulty=1,  # Fixed
            uncles_hash=EMPTY_UNCLE_HASH,  # Fixed
            mix_hash=ZERO_HASH32,  # Fixed
            nonce=b'\x00' * 8,  # Fixed
            extra_data=b"",  # Fixed
        ),
    )
    eth1_rpc.consensus_newBlock(new_block)
    header = new_block.header
    execution_payload = spec.ExecutionPayload(
        block_hash=header.hash,
        parent_hash=header.parent_hash,
        coinbase=header.coinbase,
        state_root=header.state_root,
        number=header.block_number,
        gas_limit=header.gas_limit,
        gas_used=header.gas_used,
        timestamp=header.timestamp,
        receipt_root=header.receipt_root,
        logs_bloom=b'\x00' * spec.BYTES_PER_LOGS_BLOOM,
        transactions=[],
    )

    assert _verify_execution_state_transition(execution_payload, eth1_rpc)
