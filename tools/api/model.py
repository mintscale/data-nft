from pandas import array
from pydantic import BaseModel
from bson import ObjectId

class PinnedFile(BaseModel):
    name: str
    hash: str
    gateway_url: str
    ipfs_url: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MintedFile(BaseModel):
    uri: str
    token_id: str
    token_taxon: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CarData(BaseModel):
    vin: str
    logo_name: str
    logo_uri: str
    inspection_report_uri: str
    model: str
    make: str
    manufacture_year: str
    registration_year: str
    location: list
    service_type: list
    event_type: list
    datetime: str
    gps: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MintedCarData(BaseModel):
    vin: str
    token_id: str
    car_data: CarData
    car_data_pinned: PinnedFile
    inspection_report: PinnedFile
    minted_data: MintedFile

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

