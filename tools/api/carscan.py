from typing import Dict, List
from model import CarData
from pathlib import Path
import json
import pdfkit

top = """
    <head>
        <meta name="pdfkit-page-size" content="Legal"/>
        <meta name="pdfkit-orientation" content="Landscape"/>
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
            <th>Inspection Report</th>
        </tr>
    </thead>
"""

def get_record_row(record: Dict):
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
        f"<td>{record['inspection_report_uri']}</td>"
        "</tr>"
    )

def get_record_table(record_index: int, record: Dict) -> str:
    return (
        f"<span style='font-size:20px'><i>Record {record_index}</i></span> <br/><br/>"
        f"{record_table_header}"
        "<tbody>"
        f"{get_record_row(record)}"
        "</tbody>"
        "</table>"
    )

test = """
    {
    "vin": "1234",
    "logo_name": "good",
    "logo_uri": "https://icon-library.com/images/2018/3265179_rage-meme-black-mirror-shut-up-and-dance.png",
    "inspection_report_uri": "https://aqrl.mypinata.cloud/ipfs/QmbgNJ1LvoyVQPt7BSie3M7b5s18GYTBFTDcWQS5LfVQxT",
    "model": "Honda",
    "make": "Civic",
    "manufacture_year": "2022",
    "registration_year": "2022",
    "location": [
      "USA",
      "California"
    ],
    "service_type": [
      "Regular"
    ],
    "event_type": [
      "New Car Service"
    ],
    "datetime": "01/01/2022",
    "gps": "10.10,20.20"
  },
"""
def get_certificate_html(data: List) -> str:
    record_html = ""
    index = 1
    vin = data[0]["vin"]
    logo_name = data[0]["logo_name"]
    logo_uri = data[0]["logo_uri"]
    for record in data:
        record_html += get_record_table(index, record)
        index = index + 1
    return (
        f"{top}"
        f"<img src='{logo_uri}' alt='{logo_name}' width='50' height='50'>"
        "<span style='font-size:50px; font-weight:bold'>&nbsp;Car Inspection Report</span>"
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
        # jsonpdf = pdfkit.from_string(json.dumps(data))
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