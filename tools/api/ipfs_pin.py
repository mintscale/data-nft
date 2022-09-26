from ipfs import IPFSRepo, IPFSFile
from ipfs_utils import load_config, get_logger
from pathlib import Path
from typing import Dict

def pin_to_ipfs(config: Dict, repo: IPFSRepo, filepath: Path) -> IPFSFile:
    response = repo.pin(filepath)
    retries = 3
    while not response and retries != 0:
        response = repo.pin(filepath)
        retries -= 1
    if not response:
        return None
    return IPFSFile(
                pinhash=response["IpfsHash"],
                pinsize=response["PinSize"],
                pintime=response["Timestamp"],
                pinurl=config["pinata_gateway"]+response["IpfsHash"]
            )

def pin_files(config_file, log_file, file_name: Path) -> IPFSFile:
    logger = get_logger(__name__, log_file)
    config = load_config(config_file)
    ipfs_repo = IPFSRepo(
                    api_key=config["pinata_api_key"],
                    api_secret=config["pinata_api_secret"],
                )
    if file_name.exists():
        logger.info(f"PIN[{file_name}] => IPFS")
        ipfs_file = pin_to_ipfs(config, ipfs_repo, file_name)
        if ipfs_file:
            logger.info(f"IPFS GATEWAY URL: {ipfs_file.pinurl}")
            logger.info(f"IPFS URL: ipfs://{ipfs_file.pinhash}")
            return ipfs_file
        else:
            logger.error("IPFS pin failed")
    return None