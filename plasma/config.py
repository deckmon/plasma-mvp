import os
from pathlib import Path

from dotenv import load_dotenv
from ethereum import utils


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "..", ".env"))

if os.getenv("ENV") == "LOCAL":
    plasma_config = dict(
        ROOT_CHAIN_CONTRACT_ADDRESS="0xa3b2a1804203b75b494028966c0f62e677447a39",
        NETWORK="http://localhost:8545",
        BLOCK_AUTO_SUMBITTER_INTERVAL=1,
        MAX_SNAPSHOTS=100,
        MIN_SNAPSHOT_SECONDS=15, # set 0 will not make snapshot
    )
else:
    plasma_config = dict(
        ROOT_CHAIN_CONTRACT_ADDRESS="0xC47e711ac6A3D16Db0826c404d8C5d8bDC01d7b1",
        NETWORK="http://localhost:8545",
        BLOCK_AUTO_SUMBITTER_INTERVAL=30,
        MAX_SNAPSHOTS=50,
        MIN_SNAPSHOT_SECONDS=3600, # set 0 will not make snapshot
    )

plasma_config["PICKLE_DIR"] = "child_chain_pickle"

plasma_config["BLOCK_EXPIRE_BUFFER_SECONDS"] = 600
plasma_config["TX_EXPIRE_BUFFER_SECONDS"] = plasma_config["BLOCK_EXPIRE_BUFFER_SECONDS"] + (plasma_config["BLOCK_AUTO_SUMBITTER_INTERVAL"] * 2)
plasma_config["PSTX_EXPIRE_BUFFER_SECONDS"] = plasma_config["TX_EXPIRE_BUFFER_SECONDS"] * 2

plasma_config["AUTHORITY_KEY"] = utils.normalize_key(os.getenv("AUTHORITY_KEY"))
plasma_config["AUTHORITY"] = utils.privtoaddr(plasma_config["AUTHORITY_KEY"])
plasma_config["COINBASE"] = "0x" + plasma_config["AUTHORITY"].hex()

plasma_config["CHILD_CHAIN_HOST"] = os.getenv("CHILD_CHAIN_HOST") or "0.0.0.0"
plasma_config["CHILD_CHAIN_PORT"] = os.getenv("CHILD_CHAIN_PORT") or "8546"

for env_key in [
    "CHILD_CHAIN_SSL_CRT_PATH",
    "CHILD_CHAIN_SSL_KEY_PATH",
]:
    plasma_config[env_key] = os.getenv(env_key)
