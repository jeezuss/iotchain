from chain import Chain
from config import *
from block import Block

import os
import json
import requests
import glob

def get_data(self,index):
    blocks = []
    # We're assuming that the folder and at least initial block exists
    if os.path.exists(CHAINDATA_DIR):
        for filepath in glob.glob(os.path.join(CHAINDATA_DIR, '*.json')):
            with open(filepath, 'r') as block_file:
                try:
                    block_info = json.load(block_file)
                except:
                    print(filepath)
                local_block = Block(block_info)
                blocks.append(local_block)
    blocks.sort(key=lambda block: block.index)
    local_chain = Chain(blocks)
    print(Chain.find_block_by_index(local_chain, index))


