import pytest
from eth1 import Eth1Rpc
from eth.chains.base import MiningChain, Chain
from eth.vm.forks import IstanbulVM
import eth.tools.builder.chain as builder
from copy import deepcopy

@pytest.fixture
def eth1_rpc():
    # Initialize Eth1 chain builder
    Eth1Chain = builder.build(MiningChain, builder.fork_at(IstanbulVM, 0))
    Eth1Chain = builder.enable_pow_mining(Eth1Chain)
    eth1_rpc = Eth1Rpc(Eth1Chain)
    
    return eth1_rpc


def test_initialization(eth1_rpc):
    head_block = eth1_rpc.get_head_block()
    assert head_block.header.block_number == 0


def test_consensus_assembleBlock(eth1_rpc):
    head_block = eth1_rpc.get_head_block()
    assert head_block.header.block_number == 0

    # Build a short Eth1 chain
    for i in range(13):
        eth1_rpc.consensus_assembleBlock(extra_data=b'canonical-chain')
    head_block = eth1_rpc.get_head_block()
    assert head_block.header.block_number == 13

    # Try building on an older block
    parent_hash = head_block.header.parent_hash
    new_block = eth1_rpc.consensus_assembleBlock(
        extra_data=b'fork', parent_hash=parent_hash)
    assert new_block.header.parent_hash == parent_hash
    assert new_block.header.block_number == 13


def test_consensus_newBlock(eth1_rpc):
    head_block = eth1_rpc.get_head_block()
    assert head_block.header.block_number == 0

    # Build a short Eth1 chain
    for i in range(13):
        eth1_rpc.consensus_assembleBlock(extra_data=b'canonical-chain')
    head_block = eth1_rpc.get_head_block()
    assert head_block.header.block_number == 13

    # Build longer chain in different fork in a separate instance
    new_eth1_rpc = deepcopy(eth1_rpc)
    parent_hash = head_block.header.parent_hash
    for i in range(5):
        new_block = new_eth1_rpc.consensus_assembleBlock(
            extra_data=b'fork', parent_hash=parent_hash)
        assert new_block.header.parent_hash == parent_hash
        parent_hash = new_block.header.hash
        # Import the new block in the old instance
        eth1_rpc.consensus_newBlock(new_block)
    
    assert new_block.header.block_number == 17
    assert eth1_rpc.get_head_block().header.hash == new_block.header.hash


def test_consensus_setHead(eth1_rpc):
    head_block = eth1_rpc.get_head_block()
    assert head_block.header.block_number == 0

    # Build a short Eth1 chain
    for i in range(10):
        eth1_rpc.consensus_assembleBlock(extra_data=b'canonical-chain')
    pivot_block = eth1_rpc.get_head_block()
    assert pivot_block.header.block_number == 10
    
    # Extend the canonical chain
    for i in range(10):
        eth1_rpc.consensus_assembleBlock(extra_data=b'canonical-chain')
    old_head_block = eth1_rpc.get_head_block()
    assert old_head_block.header.block_number == 20

    # Build a short fork starting at the pivot block
    parent_hash = pivot_block.header.parent_hash
    for i in range(5):
        new_block = eth1_rpc.consensus_assembleBlock(
            extra_data=b'fork', parent_hash=parent_hash)
        assert new_block.header.parent_hash == parent_hash
        parent_hash = new_block.header.hash
    # Check that canonical head has not changed
    assert eth1_rpc.get_head_block() == old_head_block

    # Set the tip of the short fork as the canonical head
    eth1_rpc.consensus_setHead(new_block.header.hash)
    assert eth1_rpc.get_head_block() == new_block

    # Build on top of the new canonical head
    additional_block = eth1_rpc.consensus_assembleBlock(extra_data=b'fork')
    assert eth1_rpc.get_head_block() == additional_block
    assert additional_block.header.parent_hash == new_block.header.hash