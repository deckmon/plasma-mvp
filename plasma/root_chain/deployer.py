import json
import os
from solc import compile_standard
from web3.contract import ConciseContract, Contract
from web3 import Web3, HTTPProvider, WebsocketProvider
from web3.middleware import geth_poa_middleware
from plasma.config import plasma_config
from plasma.utils.utils import send_transaction_sync

OWN_DIR = os.path.dirname(os.path.realpath(__file__))
CONTRACTS_DIR = OWN_DIR + '/contracts'
OUTPUT_DIR = 'contract_data'


class Deployer(object):

    def __init__(self, provider=None, CONTRACTS_DIR=CONTRACTS_DIR, OUTPUT_DIR=OUTPUT_DIR):
        if provider is None:
            if plasma_config['NETWORK'].startswith("wss://"):
                provider = WebsocketProvider(plasma_config['NETWORK'])
            else:
                provider = HTTPProvider(plasma_config['NETWORK'])
        self.w3 = Web3(provider)
        if "rinkeby" in provider.endpoint_uri:
            self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.CONTRACTS_DIR = CONTRACTS_DIR
        self.OUTPUT_DIR = OUTPUT_DIR

    def get_solc_input(self):
        """Walks the contract directory and returns a Solidity input dict

        Learn more about Solidity input JSON here: https://goo.gl/7zKBvj

        Returns:
            dict: A Solidity input JSON object as a dict
        """

        solc_input = {
            'language': 'Solidity',
            'sources': {
                file_name: {
                    'urls': [os.path.realpath(os.path.join(r, file_name))]
                } for r, d, f in os.walk(self.CONTRACTS_DIR) for file_name in f if not file_name.startswith(".")
            }
        }
        return solc_input

    def compile_all(self):
        """Compiles all of the contracts in the /contracts directory

        Creates {contract name}.json files in /build that contain
        the build output for each contract.
        """

        # Solidity input JSON
        solc_input = self.get_solc_input()

        # Compile the contracts
        compilation_result = compile_standard(solc_input, allow_paths=self.CONTRACTS_DIR)

        # Create the output folder if it doesn't already exist
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        # Write the contract ABI to output files
        compiled_contracts = compilation_result['contracts']
        for contract_file in compiled_contracts:
            for contract in compiled_contracts[contract_file]:
                contract_name = contract.split('.')[0]
                contract_data = compiled_contracts[contract_file][contract_name]

                contract_data_path = self.OUTPUT_DIR + '/{0}.json'.format(contract_name)
                with open(contract_data_path, "w+") as contract_data_file:
                    json.dump(contract_data, contract_data_file)

                contract_data_path = self.OUTPUT_DIR + '/{0}.abi.json'.format(contract_name)
                with open(contract_data_path, "w+") as contract_data_file:
                    json.dump(contract_data["abi"], contract_data_file)

    def get_contract_data(self, contract_name):
        """Returns the contract data for a given contract

        Args:
            contract_name (str): Name of the contract to return.

        Returns:
            str, str: ABI and bytecode of the contract
        """

        contract_data_path = self.OUTPUT_DIR + '/{0}.json'.format(contract_name)
        with open(contract_data_path, 'r') as contract_data_file:
            contract_data = json.load(contract_data_file)

        abi = contract_data['abi']
        bytecode = contract_data['evm']['bytecode']['object']

        return abi, bytecode

    def deploy_contract(self, contract_name, gas=5000000, args=(), concise=True):
        """Deploys a contract to the given Ethereum network using Web3

        Args:
            contract_name (str): Name of the contract to deploy. Must already be compiled.
            provider (HTTPProvider): The Web3 provider to deploy with.
            gas (int): Amount of gas to use when creating the contract.
            args (obj): Any additional arguments to include with the contract creation.
            concise (bool): Whether to return a Contract or ConciseContract instance.

        Returns:
            Contract: A Web3 contract instance.
        """

        abi, bytecode = self.get_contract_data(contract_name)

        contract_ = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        tx_receipt = send_transaction_sync(self.w3, contract_.constructor(*args))
        contract_address = tx_receipt['contractAddress']

        print("Successfully deployed {0} contract: {1}".format(contract_name, contract_address))

        contract_factory_class = ConciseContract if concise else Contract
        contract_instance = self.w3.eth.contract(abi=abi, address=contract_address, ContractFactoryClass=contract_factory_class)
        return contract_instance

    def get_contract_at_address(self, contract_name, address, concise=True):
        """Returns a Web3 instance of the given contract at the given address

        Args:
            contract_name (str): Name of the contract. Must already be compiled.
            address (str): Address of the contract.
            concise (bool): Whether to return a Contract or ConciseContract instance.

        Returns:
            Contract: A Web3 contract instance.
        """
        abi, bytecode = self.get_contract_data(contract_name)

        contract_factory_class = ConciseContract if concise else Contract
        contract_instance = self.w3.eth.contract(abi=abi, bytecode=bytecode, address=address, ContractFactoryClass=contract_factory_class)

        return contract_instance
