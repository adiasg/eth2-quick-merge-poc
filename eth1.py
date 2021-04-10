# Eth1 (py-evm) imports
from eth.chains.base import MiningChain, Chain
from eth.vm.forks import IstanbulVM
import eth.tools.builder.chain as builder
from eth.exceptions import BlockNotFound, HeaderNotFound
from eth_utils import encode_hex
from eth.constants import GENESIS_PARENT_HASH

# These are the required RPC methods from the Eth1 node
class Eth1Rpc:
    def __init__(self, chain_class):
        self.chain_class = chain_class
        self.chain = builder.genesis(self.chain_class)
    
    def consensus_assembleBlock(self, extra_data=b'', parent_hash=None):
        """
        Create new block on top of block with ``parent_hash``.
        Return the newly constructed block.
        """
        parent_header = None
        if parent_hash is not None:
            parent_header = self.chain.headerdb.get_block_header_by_hash(parent_hash)
        result = self.chain.mine_all(
            transactions=[], extra_data=extra_data, parent_header=parent_header)
        return result[0][0]

    def consensus_newBlock(self, block):
        """
        Import ``block`` into the chain.
        Return whether the block is valid.
        """
        self.chain.import_block(block)
        return True

    def consensus_setHead(self, block_hash):
        """
        Set block with ``block_hash`` as the canonical chain head.
        Returns ``True`` is successful, ``False`` otherwise.
        """
        try:
            block = self.chain.get_block_by_hash(block_hash)
        except (BlockNotFound, HeaderNotFound):
            return False
        # TODO: Validate this hacky method of setting canonical head
        self.chain.headerdb._set_as_canonical_chain_head(
            self.chain.headerdb.db, block.header, GENESIS_PARENT_HASH)
        self.chain.header = self.chain.create_header_from_parent(block.header)
        return self.chain.get_block_by_header(self.chain.get_canonical_head()).hash == block_hash

    def consensus_finaliseBlock(self, block_hash):
        pass

    def get_head_block(self):
        return self.chain.get_block_by_header(self.chain.get_canonical_head())

    def is_parent_block(self, parent_hash, block_hash):
        block = self.chain.get_block_by_hash(block_hash)
        if block.header.parent_hash == parent_hash:
            return True
        return False

    def is_accepted_block(self, block_hash):
        try:
            self.chain.get_block_by_hash(block_hash)
            return True
        except (BlockNotFound, HeaderNotFound):
            return False

    def get_score(self, block_hash):
        return self.chain.get_score(block_hash)

    def print_block(self, block, prefix=""):
        print(f"{prefix}Eth1 Block #{block.header.block_number}")
        print(f"{prefix}\tParent Hash:\t{encode_hex(block.header.parent_hash)}")
        print(f"{prefix}\tBlock Hash:\t{encode_hex(block.hash)}")
        print(f"{prefix}\tBlock Score:\t{self.get_score(block.hash)}")
