#!/usr/bin/env python3
from context import (
    XRPLAccount,
    XRPLNFT,
    get_network_url,
)

import asyncio
import json
from pathlib import Path
from xrpl.utils import hex_to_str
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import NFTokenMintFlag
from typing import List, Dict
from utils import load_config, get_logger
from model import MintedFile
from typing import Optional

async def get_mint_record(
    account: XRPLAccount,
    uri: str,
    num_records: int,
    logger,
    minted_record_file: Path = Path("minted_nfts.json"),
) -> Optional[MintedFile]:
    minted = {}
    try:
        nft_list = []
        while len(nft_list) < num_records:
            get_nfts = await account.get_nfts(limit=num_records)
            nft_list += get_nfts.result["account_nfts"]
            logger.info(f"GET_NFTS => {len(nft_list)}")
            for nft in nft_list:
                taxon = nft["NFTokenTaxon"]
                tokenID = nft["NFTokenID"]
                token_uri = hex_to_str(nft["URI"])
                minted[token_uri] = {"tokenID": tokenID, "taxon": taxon}
            if uri in minted:
                mint_record = MintedFile(uri=uri, token_id=minted[uri]["tokenID"], token_taxon=minted[uri]["taxon"])
                logger.info(f"Found Mint Record: {mint_record}")
                return mint_record
    except Exception as e:
        logger.error(f"EXCEPTION ENCOUNTERED: {e}")
    finally:
        if not minted_record_file.exists():
            minted_record_file.touch()
        with minted_record_file.open("r+", encoding="utf-8") as f:
            logger.info(f"DUMP MINTED DETAILS => {minted_record_file}")
            json.dump(minted, f, ensure_ascii=False, indent=4, sort_keys=True)
    logger.info(f"No Mint Record found for URI {uri}")
    return None

async def mint_nft_uri(
    config: Dict,
    account: XRPLAccount,
    issuer: str,
    network_url: str,
    flags: List[int],
    uri: str,
    taxon: int,
    logger,
) -> None:
    wallet = account.get_wallet()
    transfer_fee = config["transfer_fee"]
    try:
        logger.info(f"MINT[{uri}, {taxon}]")
        nft = XRPLNFT(
            issuer=issuer,
            uri=uri,
            network_url=network_url,
        )
        nft.prepare_mint_tx(
            taxon=taxon,
            flags=flags,
            transfer_fee=transfer_fee,
        )
        mint_response = await nft.mint(wallet)
        logger.info(f"RESULT {mint_response}")
    except Exception as e:
        logger.error(f"EXCEPTION ENCOUNTERED: {e}")

async def mint_nfts(uri: str, taxon: int, config_file: Path = Path("mint_config.json"), log_file: str = "mint_nft.log") -> Optional[MintedFile]:
    logger = get_logger(__name__, log_file)
    config = load_config(config_file)
    xrpl_account = config["xrpl_account"]
    xrpl_secret = config["xrpl_secret"]
    network_url = get_network_url(mode="devnet")
    acc = XRPLAccount(xrpl_secret, network_url)
    await mint_nft_uri(
        config=config,
        account=acc,
        issuer=xrpl_account,
        network_url=network_url,
        flags=[NFTokenMintFlag.TF_TRANSFERABLE, NFTokenMintFlag.TF_ONLY_XRP],
        uri=uri,
        taxon=taxon,
        logger=logger
    )
    mint_record : Optional[MintedFile] = await get_mint_record(
        account=acc,
        uri=uri,
        num_records=100,
        logger=logger,
    )
    return mint_record

