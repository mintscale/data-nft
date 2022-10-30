from typing import Dict, List
from model import CarData
from pathlib import Path
import json
import pdfkit

top = """
    <head>
        <meta name="pdfkit-page-size" content="Legal"/>
        <meta name="pdfkit-orientation" content="Landscape"/>
        <script src="https://kit.fontawesome.com/yourcode.js" crossorigin="anonymous"></script>
    </head>
"""

options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    'no-outline': None
}

record_table_header = """
<table class="styled-table">
    <thead>
        <tr>
            <th>Date</th>
            <th>Location</th>
            <th>GPS</th>
            <th>Make</th>
            <th>Model</th>
            <th>Manufacture Year</th>
            <th>Registration Year</th>
            <th>Service Type</th>
            <th>Event Type</th>
            <th>Event Report</th>
            <th>NFT Certificate</th>
            <th>IPFS Metadata</th>
        </tr>
    </thead>
"""
ipfs_logo_src = "src='https://upload.wikimedia.org/wikipedia/commons/1/18/Ipfs-logo-1024-ice-text.png' width='20' height='20'"
nft_logo_src = "src='https://cdn-icons-png.flaticon.com/512/6298/6298900.png' width='25' height='25'"

NFT_DEVNET_EXPLORER_ROOT="https://nft-devnet.xrpl.org/nft"

def get_car_record_row(token_id: str, record: Dict, inspection_report_pin: Dict, car_record_pin: Dict):
    return (
        "<tr>"
        f"<td>{record['datetime']}</td>"
        f"<td>{', '.join(record['location'])}</td>"
        f"<td>{record['gps']}</td>"
        f"<td>{record['make']}</td>"
        f"<td>{record['model']}</td>"
        f"<td>{record['manufacture_year']}</td>"
        f"<td>{record['registration_year']}</td>"
        f"<td>{', '.join(record['service_type'])}</td>"
        f"<td>{', '.join(record['event_type'])}</td>"
        f"<td><a href={inspection_report_pin['gateway_url']}><img alt='Event Report' {ipfs_logo_src}></a></td>"
        f"<td><a href={NFT_DEVNET_EXPLORER_ROOT}/{token_id}><img alt='NFT Certificate' {nft_logo_src}></a></td>"
        f"<td><a href={car_record_pin['gateway_url']}><img alt='Event Metadata' {ipfs_logo_src}></a></td>"
        "</tr>"
    )

def get_record_table(
    record_index: int, 
    token_id: str,
    car_record_pin:  Dict,
    inspection_report_pin:  Dict,
    car_record: Dict,
    minted_data: Dict,
) -> str:
    return (
        f"<span style='font-size:20px'><i>Record {record_index}</i></span> <br/><br/>"
        f"{record_table_header}"
        "<tbody>"
        f"{get_car_record_row(token_id, car_record, inspection_report_pin, car_record_pin)}"
        "</tbody>"
        "</table>"
    )

def get_certificate_html(data: List) -> str:
    record_html = ""
    index = 1
    car_data = data[0]["car_data"]
    vin = car_data["vin"]
    logo_name = car_data["logo_name"]
    logo_uri = car_data["logo_uri"]
    for mint_record in data:
        token_id = mint_record["token_id"]
        car_record_pin = mint_record["car_data_pinned"]
        inspection_report_pin = mint_record["inspection_report"]
        car_record = mint_record["car_data"]
        minted_data = mint_record["minted_data"]
        record_html += get_record_table(
            index,
            token_id,
            car_record_pin,
            inspection_report_pin,
            car_record,
            minted_data
        )
        index = index + 1
    return (
        f"{top}"
        f"<img src='{logo_uri}' alt='{logo_name}' width='50' height='50'>"
        "<span style='font-size:50px; font-weight:bold'>&nbsp;Carscan Inspection Report</span>"
        "<br/><br/>"
        f"<span style='font-size:30px'>VIN {vin}</span> <br/><br/>"
        f"{record_html}"
        '</div>'
        '</div>'
    )

def parse_metadata_json(metadata_json: Path) -> Dict:
    data = {}
    with metadata_json.open("r") as metafile:
        data = json.load(metafile)
    return data

def generate_pdf_report(data: List, filepath: Path):   
    with filepath.open("wb") as file:
        jsonpdf = pdfkit.from_string(get_certificate_html(data), options=options, css='styled-table.css')
        file.write(jsonpdf)

async def process_car_event(vin: str, logo_name: str, logo_uri: str, inspection_report_uri: str, metadata_json: Path) -> CarData:
    metadata = parse_metadata_json(metadata_json)
    record : CarData = CarData(
        vin=vin,
        logo_name=logo_name,
        logo_uri=logo_uri,
        inspection_report_uri=inspection_report_uri,
        model=metadata["model"],
        make=metadata["make"],
        manufacture_year=metadata["manufacture_year"],
        registration_year=metadata["registration_year"],
        location=metadata["location"],
        service_type=metadata["service_type"],
        event_type=metadata["event_type"],
        datetime=metadata["datetime"],
        gps=metadata["gps"],
    )
    print(f"processed: {record}")
    return record