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
- *requirements.txt*: Python dependency list used by pip to install dependencies
- *Makefile*: Install deps and run api
- *setup.py*: Package setup file for future use


## Initialize Dependencies

In order to run the data NFT REST API locally, first install the required packages and create a Python Virtual Env by running:
    
    $ make init

This will create a directory `ms` at the top level and install all the dependencies in there. The first run will take some time. Consecutive runs will be faster.

## Configuration

In order to run the API, an environment variable `MONGODB_URL` will need to be exported first. This should have the format:

```
export MONGODB_URL="mongodb+srv://<username>:<password>@<clusterID>.mongodb.net/<Cluster>?retryWrites=true&w=majority"
```

Create a MONGO DB instance and add in the credentials to the above command and run it in your shell. At this point another configuration file `mint_config.json` is required in the `tools/api` directory. It needs the following fields:

```
{
    "pinata_api_key": "",
    "pinata_api_secret": "",
    "pinata_gateway": "",
    "xrpl_account": "",
    "xrpl_secret": "",
    "transfer_fee": 1000
}
```

Populate these fields and save the file in the api directory to complete configuration.

## Run the REST API

Once configuration is complete, run the API by doing:

    $ make api

This will initialize the API to be active at `http://127.0.0.1:8000` i.e. on localhost. 