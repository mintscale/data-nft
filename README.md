# MintScale Automotive Data NFT

## Overview

Data NFTs are an intellectual property bundle comprising:

1. A public NFT
2. Linked to a permissioned data event stored on IPFS
3. Governed by a private license granting ownership and access rights

This repo uses the XRP Ledger to help mint Data NFTs for the Auotomotive Industry. It provides a grounds up libraries for:

1. XRPL NFT mint Operations
2. IPFS Hosting Utilities
3. NFT Collection Minting Composite Functions
4. FASTAPI + MongoDB based Rest API to mint Data NFTs and create PDF Event History Certificates

## Repo Structure

- *aqrl_xrpl*: NFT library providing minting constructs using XRPL
- *docs*: Code Documentation Sources
- *scripts*: Custom scripts for ad-hoc minting
- *site*: Scaffold Node-JS site to test mint functionality
- *tests*: XRPL library unit tests
- *tools*: Standalone tools to create and manage Data NFTs and NFT Collections
    - *api*: FASTAPI based REST API for creating, storing, updating and retreiving Data NFTs
    - *ipfs*: IPFS pin, unpin, list files using Pinata
    - *minter*: Define, Pin and Mint an NFT Collection on XRPL
    - *signoz*: Submodule for FASTAPI Health Monitoring Dashboard


## Build

To build and test locally:

    $ make init
    $ make test
