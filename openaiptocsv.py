try:
    from google.cloud import storage
except:
    print("You need to install the requirements. See requirements.txt and use 'pip install -r requirements.txt' to install it")
import json
import sys
import csv
import sys
import argparse
import os.path
from pathlib import Path

PROGRAM_VERSION = 1.3

destination_file_name = Path(".", "openAIP_files")
destination_csv_file_name = Path(".", "Userpoints") 

bucket_name = "29f98e10-a489-4c82-ae5e-489dbcd4912f"  # see OpenAIP documentation

def set_folders():
    openAIP_folder = Path(".", "openAIP_files")
    if not openAIP_folder.exists:
        openAIP_folder.mkdir()
        print("Folder created {}".format(destination_file_name.absolute()))
    print(destination_file_name)
    return 

class state:
    static = 0
    variable = 1
    calculated = 2
    listed = 3
    dictonary = 4
    airport = 5

def download_public_file(countries=None):
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(bucket_name)
    for country in countries:
        source_blob_names = [country + "_apt.json", country + "_rpp.json"]
        found = None
        for blob1 in source_blob_names:
            blob = bucket.blob(blob1)
            try:
                blob.download_to_filename(Path(destination_file_name, blob1))
                print(
                    "Downloaded file {} into folder {}".format(blob.name, destination_file_name.absolute())
                )
                found = True
            except:
                pass
        if not found:
            print(
                "No files for country {}. Please use only 2 letter formated ISO-Country codes".format(country)
            )

def read_points(id=None, country=None):
    source_blob_names = [country + "_apt.json", country + "_rpp.json"]
    id = id
    point_list = []
    with open(Path(destination_file_name, source_blob_names[1]), "r", encoding="utf8") as f:
        structure = json.load(f)
    for point in structure:
        for airport in point["airports"]:
            try:
                if airport == id["_id"]:
                    print("Found: {}".format(point["name"]))
                    point_list.append(point)
            except:
                pass
    return point_list

def find_airport(icao=None, name=None, country=None):
    source_blob_names = [country + "_apt.json", country + "_rpp.json"]
    icao = icao
    country = country
    if not icao:
        name = name
        print("Searching for {} in country {}".format(name, country))
    else:
        print("Searching for {} in country {}".format(icao, country))
    with open(Path(destination_file_name, source_blob_names[0]), "r", encoding="utf8") as f:
        structure = json.load(f)
    for apt in structure:
        try:
            if apt["icaoCode"] == icao or apt["name"] == name:
                return apt
        except:
            pass
    print("Not found")
    return None


def write_csv(waypoints, airport_ids, country):
    columns = ["Type", "Name", "Ident", "Latitude", "Longitude", "Elevation", "Magnetic Declination",
               "Tags", "Description", "Region", "Visible From", "Last Edit", "Import Filename"]
    mapping = {"Type": [state.static, "VRP"],
               "Name": [state.variable, "name"],
               "Ident": [state.calculated, ""],
               "Latitude": [state.listed, "geometry", "coordinates", 1],
               "Longitude": [state.listed, "geometry", "coordinates", 0],
               "Elevation": [state.dictonary, "elevation", "value"],
               "Magnetic Declination": [state.airport, "magneticDeclination", None, None],
               "Tags": [state.airport, "icaoCode", state.variable, "compulsory"],
               "Description": [state.static, "Reporting Point from https://www.openaip.net/"],
               "Region": [state.variable, "country"],
               "Visible from": [state.static, "25"],
               "Last Edit": [state.variable, "updatedAt"],
               "Import Filename": [state.static, ""]
               }
    entries = []
    for wp in waypoints:
        object = {}
        for key, entry in mapping.items():
            match entry[0]:
                case state.static:
                    object[key] = entry[1]
                case state.variable:
                    object[key] = wp[entry[1]]
                case state.calculated:
                    if key == "Ident":
                        object[key] = ""
                    else:
                        object[key] = ""
                case state.listed:
                    outer = wp[entry[1]]
                    inner = outer[entry[2]]
                    object[key] = inner[entry[3]]
                case state.airport:
                    apt_id = wp["airports"][0]
                    for apt in airport_ids:
                        try:
                            if apt["_id"] == apt_id:
                                object[key] = apt[entry[1]]
                                if entry[2] == state.variable:
                                    if wp[entry[3]]:
                                        object[key] += " Compulsory"
                        except:
                            pass
                case state.dictonary:
                    outer = dict(wp[entry[1]])
                    object[key] = outer[entry[2]]
                case _:
                    object[key] = ""

        entries.append(object)
    if entries:
        file = Path(destination_csv_file_name, country + ".csv")
        with open(file, "w+", newline="") as out_file:
            csv_w = csv.DictWriter(out_file, entries[0].keys())
            csv_w.writeheader()
            for i in entries:
                csv_w.writerow(i)

def find_all_airports(country=None):
    source_blob_names = [country + "_apt.json", country + "_rpp.json"]
    airport_ids = []
    if os.path.exists(Path(destination_file_name, source_blob_names[0])):
        with open(Path(destination_file_name, source_blob_names[0]), "r", encoding="utf8") as f:
            structure = json.load(f)
        for apt in structure:
            try:
                if apt["type"] != 7:
                    airport_ids.append(apt)
            except:
                pass
    else:
        print("there is no downloaded file for country {}".format(country)) 
    return airport_ids


def read_all_points(airport_ids=None, country=None):
    point_list = []
    for airport in airport_ids:
        print("Looking for airport: {}".format(airport["name"]))
        point_list += read_points(airport, country)
    return point_list

def identify_all_json():
    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(bucket_name)
    countries = []
    for blob in bucket.list_blobs():
        if "rpp.json" in blob.name: 
            countries.append(blob.name[0:2])
            print(
                "Country {}".format(blob.name[0:2])
            )
    return countries

def main() -> int:
    """Main function according to passed arguments"""
    parser = argparse.ArgumentParser(
        description="""\
    Download json files from OpenAIP stored on Google
    and convert it to CSV for Little Navmap""",
        epilog="Working directory             : " + str(destination_file_name.absolute()) 
        + "\n\rOutput directory for csv files: " + str(destination_csv_file_name.absolute())
        + "\n\rExample: %(prog)s -d DE                will download the data for Germany"
        + "\n\r         %(prog)s -i EDDK EDDL -c DE   will generate the user points for Cologne and Duesseldorf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="Openaiptocsv")
    group = parser.add_argument_group(title="Download functions",description="Use these functions first to download the needed openAIP files")
    group.add_argument("-da", "--download_all", help="Downloads all available data", action="store_true")
    group.add_argument("-d", "--download", action="store", nargs="*", help="Downloads the listed countries")
    group2 = parser.add_argument_group(title="Create CSV files",description="After downloading you could extract single or multiple csv files")
    group2.add_argument("-i", "--icaoCode", action="store", nargs="*", help="Creates a csv containing the listed airports out of a specified country")
    group2.add_argument("-n", "--name", action="store", nargs="*", help="Creates a csv containing the listed airports matching the name")
    group2.add_argument("-w", "--writeCountry", action="store", nargs="*", help="Writes the csv file for the entire country / countries")
    group2.add_argument("-c", "--country", action="store", nargs="?", help="Specify the country for the icao code or name you are searching for")
    parser.add_argument("--version", action="version", version="%(prog)s " + str(PROGRAM_VERSION))
    args = parser.parse_args()
    destination_file_name.mkdir(exist_ok=True)
    destination_csv_file_name.mkdir(exist_ok=True)  
    if args.download_all:
        print("Download all needed data from Google")
        countries = identify_all_json()
        download_public_file(countries)
    if args.download:
        download_public_file(args.download)
    if args.writeCountry:
        for country_raw in args.writeCountry:
            country = country_raw.upper()
            print("create {0}".format(country))
            airport_ids = find_all_airports(country)
            point_list = read_all_points(airport_ids, country)
            write_csv(point_list, airport_ids, country)
    if args.icaoCode and args.country:
        airport_ids = []
        waypoints = []
        country = args.country.upper()
        for icao in args.icaoCode:
            airport_id = find_airport(icao=icao.upper(), name=None, country=country)
            airport_ids.append(airport_id)
            waypoints += read_points(airport_id, country)
        write_csv(waypoints, airport_ids, country)
    if args.name and args.country:
        airport_ids = []
        waypoints = []
        country = args.country.upper()
        for name in args.name:
            airport_id = find_airport(icao=None, name=name.upper(), country=country)
            airport_ids.append(airport_id)
            waypoints += read_points(airport_id, country)
        write_csv(waypoints, airport_ids, country)
    if (args.icaoCode or args.name) and not args.country:
        print("Please specify a country for those airports using '-c'")
    v = vars(args)     
    if  sum([ 1 for a in v.values( ) if a]) == 0:
        parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())

