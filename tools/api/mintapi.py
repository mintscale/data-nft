#!/usr/bin/env python3
from numpy import isposinf
from ipfs_pin import pin_files
from mint_nft import mint_nfts
from db import (
    fetch_one_car_by_vin,
    fetch_all_car_records_by_vin,
    fetch_one_pinned_file_by_hash,
    fetch_one_minted_file_by_uri,
    fetch_all_pinned_files,
    fetch_all_minted_files,
    create_pinned_file,
    create_minted_file,
    create_car_record,
    remove_pinned_file_by_hash,
    remove_minted_file_by_uri,
)
from ipfs import IPFSFile
from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, Body, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from model import PinnedFile, MintedFile, CarData
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from carscan import process_car_event, generate_pdf_report
import tempfile
from starlette.background import BackgroundTask
import os

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path

def get_db_file(name: str, file: IPFSFile) -> PinnedFile:
    return PinnedFile(name=name, hash=file.pinhash, gateway_url=file.pinurl, ipfs_url=f"ipfs://{file.pinhash}")

@app.get("/")
async def health_check():
    return {"Hello":"Crypto Wizards!"}


@app.get("/api/ipfs/pinned")
async def get_pinned_files():
    response = await fetch_all_pinned_files()
    return response

@app.get("/api/ipfs/pinned/{hash}", response_model=PinnedFile)
async def get_pinned_file_by_hash(hash: str):
    response = await fetch_one_pinned_file_by_hash(hash)
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Pinned Files with hash: {hash}")

@app.post("/api/ipfs/pin", response_model=PinnedFile)
async def pin_file_to_ipfs(upload_file: UploadFile):
    tmp_path = save_upload_file_tmp(upload_file)
    try:
        pinned_file : IPFSFile = pin_files(config_file=Path("config.json"), log_file="ipfs_pin.log", file_name=tmp_path)
        if pinned_file:
            db_file = get_db_file(upload_file.filename, pinned_file)
            db_file_e = jsonable_encoder(db_file)
            response = await create_pinned_file(db_file_e)
            if response.acknowledged:
                print(f"Inserted {response.inserted_id} with file {db_file.name}, hash {db_file.hash}")
                created = await fetch_one_pinned_file_by_hash(db_file.hash)
                return created
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pin Failed")    
    finally:
        tmp_path.unlink()

@app.delete("/api/ipfs/remove/{hash}")
async def delete_pinned_from_db(hash: str):
    response = await remove_pinned_file_by_hash(hash)
    if response:
        return f"Successfully deleted Pinned from DB: {hash}"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Pinned File with Hash: {hash}")

@app.get("/api/nft/minted")
async def get_minted_files():
    response = await fetch_all_minted_files()
    return response

@app.get("/api/nft/minted/{uri}", response_model=MintedFile)
async def get_minted_file_by_uri(uri: str):
    response = await fetch_one_minted_file_by_uri(uri)
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Minted files with URI: {uri}")

@app.get("/api/car/json/{vin}")
async def get_car_records_by_vin_json(vin: str):
    response = await fetch_all_car_records_by_vin(vin)
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cars with vin: {vin}")

@app.get("/api/car/pdf/{vin}",response_class=FileResponse)
async def get_car_records_by_vin_pdf(vin: str):
    response = await fetch_all_car_records_by_vin(vin)
    if response:
        # file = tempfile.NamedTemporaryFile(suffix=".pdf")
        filepath = Path("./record.pdf")
        data = jsonable_encoder(response)
        generate_pdf_report(data, filepath)
        return filepath.resolve()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cars with vin: {vin}")

@app.post("/api/nft/mint", response_model=MintedFile)
async def mint_file(uri: str, taxon: int):
    mint_record = await mint_nfts(uri=uri, taxon=taxon)
    db_file_e = jsonable_encoder(mint_record)
    response = await create_minted_file(db_file_e)
    if response.acknowledged:
        print(f"Inserted {response.inserted_id} with file {mint_record.uri}, tokenID {mint_record.token_id}")
        created = await fetch_one_minted_file_by_uri(mint_record.uri)
        return created
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Mint Failed")

@app.post("/api/car/event", response_model=CarData)
async def record_car_event(vin: str, logo_name: str, logo_uri: str, inspection_report_uri: str, metadata_json: UploadFile):
    tmp_metadata_path = save_upload_file_tmp(metadata_json)
    car_record = await process_car_event(
        vin=vin, 
        logo_name=logo_name, 
        logo_uri=logo_uri,
        inspection_report_uri=inspection_report_uri,
        metadata_json=tmp_metadata_path)
    db_file_e = jsonable_encoder(car_record)
    response = await create_car_record(db_file_e)
    if response.acknowledged:
        print(f"Inserted {response.inserted_id} with car {car_record.vin}")
        created = await fetch_one_car_by_vin(car_record.vin)
        return created
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Car Record Entry Failed")

@app.delete("/api/nft/remove/{uri}")
async def delete_mint_from_db(uri: str):
    response = await remove_minted_file_by_uri(uri)
    if response:
        return f"Successfully deleted Minted URI from DB: {uri}"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Minted File with URI: {uri}")
