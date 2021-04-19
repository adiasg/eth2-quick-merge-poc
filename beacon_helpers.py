from typing import Optional

from eth.rlp.headers import BlockHeader
from eth.constants import (
    ZERO_HASH32,
    EMPTY_UNCLE_HASH,
    BLANK_ROOT_HASH,
)
from eth.vm.forks.berlin.transactions import (
    BerlinTransactionBuilder,
)
from eth.db.trie import make_trie_root_and_nodes

import eth2spec.merge.spec as spec


#
# Beacon chain
#
def _get_pow_block(block_hash: spec.Hash32, _eth1_rpc: Optional['Eth1Rpc'] = None) -> spec.PowBlock:
    # Workaroud: since the stub interface doesn't pass `eth1_rpc`, use global eth1_rpc
    global eth1_rpc
    # Pytest
    if _eth1_rpc != None:
        eth1_rpc = _eth1_rpc

    pow_block = spec.PowBlock(
        block_hash=block_hash,
        is_processed=False,
        is_valid=False,
        total_difficulty=0,
    )
    if eth1_rpc.is_accepted_block(block_hash):
        block = eth1_rpc.get_block_by_hash(block_hash)
        pow_block.is_processed = True
        pow_block.is_valid = True
        pow_block.total_difficulty = eth1_rpc.get_score(block_hash)
    return pow_block


def _verify_execution_state_transition(execution_payload: spec.ExecutionPayload, _eth1_rpc: Optional['Eth1Rpc'] = None) -> bool:
    # Workaroud: since the stub interface doesn't pass `eth1_rpc`, use global eth1_rpc
    global eth1_rpc
    # Pytest
    if _eth1_rpc != None:
        eth1_rpc = _eth1_rpc

    # Compute transaction_root
    txs = []
    for opaque_tx in execution_payload.transactions:
        decoded_tx = BerlinTransactionBuilder.deserialize(opaque_tx)
        txs.append(decoded_tx)
    transaction_root, _ = make_trie_root_and_nodes(txs)

    # Verify block hash is correct
    pow_block_header = BlockHeader(
        difficulty=1,
        block_number=execution_payload.number,
        gas_limit=execution_payload.gas_limit,
        timestamp=execution_payload.timestamp,
        coinbase=execution_payload.coinbase,
        parent_hash=execution_payload.parent_hash,
        uncles_hash=EMPTY_UNCLE_HASH,
        state_root=execution_payload.state_root,
        transaction_root=transaction_root,
        receipt_root=execution_payload.receipt_root,
        bloom=0,  # TODO
        gas_used=execution_payload.gas_used,
        extra_data=b'',
        mix_hash=ZERO_HASH32,
        nonce=b'\x00' * 8,
    )
    if execution_payload.block_hash != pow_block_header.hash:
        return False

    # Assumption: Eth1 p2p has gossiped the block already
    return eth1_rpc.is_accepted_block(execution_payload.block_hash)


#
# Validator
#
def _get_pow_chain_head() -> spec.PowBlock:
    return eth1_rpc.get_head_block()


def _produce_execution_payload(parent_hash: spec.Hash32, timestamp: spec.uint64) -> spec.ExecutionPayload:
    ...
