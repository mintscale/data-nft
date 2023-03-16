#!/usr/bin/env python3
from numpy import isposinf
import json
import random
from ipfs_pin import pin_files
from mint_nft import mint_nfts
from db import (
    fetch_one_minted_car_by_vin_token_id,
    fetch_one_pinned_file_by_hash,
    fetch_one_minted_file_by_uri,
    fetch_all_pinned_files,
    fetch_all_minted_files,
    fetch_all_minted_car_records_by_vin,
    create_pinned_file,
    create_minted_file,
    create_minted_car_record,
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
from model import PinnedFile, MintedFile, CarData, MintedCarData
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from carscan import process_car_event, parse_metadata_json, missing_metadata_keys, generate_pdf_report
import tempfile
from starlette.background import BackgroundTask
import os
import requests
import PyPDF2

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

def remove_last_page_pdf(pdf: Path):
    # Open the PDF file
    with pdf.open("rb") as pdf_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Get the number of pages in the PDF file
        num_pages = len(pdf_reader.pages)
        # Create a PDF writer object
        pdf_writer = PyPDF2.PdfWriter()
        # Add all pages to the writer except the last one
        for page in range(num_pages - 1):
            pdf_writer.add_page(pdf_reader.pages[page])
        # Save the new PDF file
        with open(pdf.name, 'wb') as new_file:
            pdf_writer.write(new_file) 

def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path

def save_car_data_tmp(car_data: CarData) -> Path:
    try:
        with NamedTemporaryFile(delete=False, mode='w', suffix=".json") as tmp:
            tmp.write(car_data.json())
            tmp.flush()
            tmp_path = Path(tmp.name)
    except Exception as e:
        print(f"DEBUG: Exception in json writing: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to write CarData JSON")
    return tmp_path

def save_uri_file_tmp(uri: str) -> Path:
    try:
        with NamedTemporaryFile(delete=False) as tmp:
            print(f"DEBUG: tmp file: {tmp.name}")
            response = requests.get(uri, stream=True)
            print(f"DEBUG: get: {response}")
            if response.status_code == 200:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, tmp)
                tmp_path = Path(tmp.name)
            else:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to fetch URI {uri}")  
    except:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to save URI {uri} to tmp file") 
    return tmp_path

@app.post("/api/ipfs/pincardata", response_model=PinnedFile, include_in_schema=False)
async def pin_car_data_to_ipfs(car_data: CarData):
    tmp_path = save_car_data_tmp(car_data)
    try:
        pinned_file : IPFSFile = pin_files(config_file=Path("config.json"), log_file="ipfs_pin.log", file_name=tmp_path)
        if pinned_file:
            db_file = get_db_file(tmp_path.name, pinned_file)
            db_file_e = jsonable_encoder(db_file)
            response = await create_pinned_file(db_file_e)
            if response.acknowledged:
                print(f"Inserted {response.inserted_id} with file {db_file.name}, hash {db_file.hash}")
                created = await fetch_one_pinned_file_by_hash(db_file.hash)
                return created
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pin Car Data Failed")    
    finally:
        tmp_path.unlink() 

def get_db_file(name: str, file: IPFSFile) -> PinnedFile:
    return PinnedFile(name=name, hash=file.pinhash, gateway_url=file.pinurl, ipfs_url=f"ipfs://{file.pinhash}")

@app.get("/")
async def health_check():
    return {"Hello":"Crypto Wizards!"}


@app.get("/api/ipfs/pinned", include_in_schema=False)
async def get_pinned_files():
    response = await fetch_all_pinned_files()
    return response

@app.get("/api/ipfs/pinned/{hash}", response_model=PinnedFile, include_in_schema=False)
async def get_pinned_file_by_hash(hash: str):
    response = await fetch_one_pinned_file_by_hash(hash)
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Pinned Files with hash: {hash}")

@app.post("/api/ipfs/pin", response_model=PinnedFile, include_in_schema=False)
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

@app.post("/api/ipfs/pinuri", response_model=PinnedFile, include_in_schema=False)
async def pin_uri_to_ipfs(uri: str):
    tmp_path = save_uri_file_tmp(uri)
    try:
        pinned_file : IPFSFile = pin_files(config_file=Path("config.json"), log_file="ipfs_pin.log", file_name=tmp_path)
        if pinned_file:
            db_file = get_db_file(uri, pinned_file)
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


@app.delete("/api/ipfs/remove/{hash}", include_in_schema=False)
async def delete_pinned_from_db(hash: str):
    response = await remove_pinned_file_by_hash(hash)
    if response:
        return f"Successfully deleted Pinned from DB: {hash}"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Pinned File with Hash: {hash}")

@app.get("/api/nft/minted", include_in_schema=False)
async def get_minted_files():
    response = await fetch_all_minted_files()
    return response

@app.get("/api/nft/minted/{uri}", response_model=MintedFile, include_in_schema=False)
async def get_minted_file_by_uri(uri: str):
    response = await fetch_one_minted_file_by_uri(uri)
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Minted files with URI: {uri}")

@app.get("/api/car/json/{vin}")
async def get_car_records_by_vin_json(vin: str):
    response = await fetch_all_minted_car_records_by_vin(vin)
    if response:
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cars with vin: {vin}")

@app.get("/api/car/pdf/{vin}",response_class=FileResponse)
async def get_car_records_by_vin_pdf(vin: str):
    response = await fetch_all_minted_car_records_by_vin(vin)
    if response:
        filepath = Path("./record.pdf")
        data = jsonable_encoder(response)
        generate_pdf_report(data, filepath)
        remove_last_page_pdf(filepath)
        return filepath.resolve()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cars with vin: {vin}")

@app.post("/api/nft/mint", response_model=MintedFile, include_in_schema=False)
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

@app.post("/api/car/event", response_model=MintedCarData)
async def record_car_event(vin: str, logo_name: str, logo_uri: str, inspection_report_uri: str, metadata_json: UploadFile):
    tmp_metadata_path = save_upload_file_tmp(metadata_json)
    inspection_report_pinned : PinnedFile = await pin_uri_to_ipfs(inspection_report_uri)
    metadata = parse_metadata_json(tmp_metadata_path)
    missing_keys = missing_metadata_keys(metadata=metadata)
    if len(missing_keys) > 0:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing entries in metadata json: {missing_keys}") 
    car_record : CarData = await process_car_event(
        vin=vin, 
        logo_name=logo_name, 
        logo_uri=logo_uri,
        inspection_report_uri=inspection_report_pinned["ipfs_url"],
        metadata=metadata)
    car_data_pinned : PinnedFile = await pin_car_data_to_ipfs(car_record)
    car_data_nft : MintedFile = await mint_file(uri=car_data_pinned["ipfs_url"], taxon=random.randint(1, 2147483647))
    minted_record : MintedCarData = MintedCarData(
        vin=vin,
        token_id=car_data_nft["token_id"],
        car_data=car_record,
        car_data_pinned=car_data_pinned,
        inspection_report=inspection_report_pinned,
        minted_data=car_data_nft,
    )
    db_file_e = jsonable_encoder(minted_record)
    response = await create_minted_car_record(db_file_e)
    if response.acknowledged:
        print(f"Inserted {response.inserted_id} with car {minted_record.vin} and NFT Token {minted_record.token_id}")
        created = await fetch_one_minted_car_by_vin_token_id(minted_record.vin, minted_record.token_id)
        return created
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Car Record Entry Failed")

@app.delete("/api/nft/remove/{uri}", include_in_schema=False)
async def delete_mint_from_db(uri: str):
    response = await remove_minted_file_by_uri(uri)
    if response:
        return f"Successfully deleted Minted URI from DB: {uri}"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Minted File with URI: {uri}")
