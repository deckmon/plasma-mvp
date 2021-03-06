#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import json
import subprocess
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )

from plasma.config import plasma_config
from plasma_tools.deployment import deploy
from plasma_tools.config import tools_config
from plasma_tools.test import erc20_contract


def process_cmd(command, raise_exception=True):
    command = "python plasma_tools/cli.py %s" % command
    print("cmd: " + command)
    status, output = subprocess.getstatusoutput(command)
    if status != 0 and raise_exception:
        raise Exception(output)
    print(output)
    return status, output


def main():
    deploy()
    erc20_contract.approve(plasma_config['ROOT_CHAIN_CONTRACT_ADDRESS'], 1000000000, transact={'from': plasma_config['COINBASE']})
    process_cmd("deposit {0} 1000000000 0 {1}".format(tools_config["ERC20_CONTRACT_ADDRESS"],plasma_config['COINBASE']))
#     process_cmd("submitblock 3bb369fecdc16b93b99514d8ed9c2e87c5824cf4a6a98d2e8e91b7dd0c063304")
    process_cmd("balance {0} latest".format(plasma_config['COINBASE']))


if __name__ == '__main__':
    main()