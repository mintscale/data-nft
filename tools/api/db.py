from model import PinnedFile, MintedFile, CarData
import os
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
database = client.AQRL
pin_collection = database.IPFSPinnedFiles
mint_collection = database.XRPLMintedFiles
car_collection = database.CARScanDB

async def fetch_one_car_by_vin(vin: str):
    document = await car_collection.find_one({"vin": vin})
    return document 

async def fetch_one_pinned_file_by_name(name: str):
    document = await pin_collection.find_one({"name": name})
    return document 

async def fetch_one_pinned_file_by_hash(hash: str):
    document = await pin_collection.find_one({"hash": hash})
    return document 

async def fetch_one_minted_file_by_uri(uri: str):
    document = await mint_collection.find_one({"uri": uri})
    return document 

async def fetch_one_minted_file_by_token_id(token_id: str):
    document = await mint_collection.find_one({"token_id": token_id})
    return document 

async def fetch_all_cars():
    cars = []
    cursor = car_collection.find({})
    async for document in cursor:
        cars.append(CarData(**document))
    return cars

async def fetch_all_car_records_by_vin(vin: str):
    cars = []
    cursor = car_collection.find({"vin": vin})
    async for document in cursor:
        cars.append(CarData(**document))
    return cars

async def fetch_all_pinned_files():
    pinned_files = []
    cursor = pin_collection.find({})
    async for document in cursor:
        pinned_files.append(PinnedFile(**document))
    return pinned_files

async def fetch_all_minted_files():
    minted_files = []
    cursor = mint_collection.find({})
    async for document in cursor:
        minted_files.append(MintedFile(**document))
    return minted_files  

async def create_car_record(car_data):
    document = car_data
    result = await car_collection.insert_one(document)
    return result

async def create_pinned_file(pinned_file):
    document = pinned_file
    result = await pin_collection.insert_one(document)
    return result

async def create_minted_file(minted_file):
    document = minted_file
    result = await mint_collection.insert_one(document)
    return result

async def remove_car_by_vin(vin):
    await car_collection.delete_one({"vin": vin})
    return True

async def remove_pinned_file_by_name(name):
    await pin_collection.delete_one({"name": name})
    return True

async def remove_pinned_file_by_hash(hash):
    await pin_collection.delete_one({"hash": hash})
    return True

async def remove_minted_file_by_uri(uri):
    await mint_collection.delete_one({"uri": uri})
    return True

async def remove_minted_file_by_token_id(token_id):
    await mint_collection.delete_one({"token_id": token_id})
    return True