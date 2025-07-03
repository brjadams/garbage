import oracledb
import argparse
import requests
from requests.auth import HTTPBasicAuth
 
parser = argparse.ArgumentParser(description="Connect to Oracle DB and fetch data")
parser.add_argument('--user', required=True, help='Username for the database')
parser.add_argument('--password', required=True, help='Password for the database')
parser.add_argument('--dsn', required=True, help='Data Source Name (host:port/service_name)')
args = parser.parse_args()
 
def get_overlay_list() -> list[str]:
    try:
        url_userid= "pdpUser"
        url_pwd = "uoDguZfAQvMEk6nExdD"
        url = "https://hcms-stage.landsend-dam.com/hcms/v4.2/entity/pdpImage?query=pdpImageCaptionLastModificationDate%3E%222025-04-19T00:00:00Z%22"  
 
        response = requests.get(url, verify=False, auth=HTTPBasicAuth(url_userid, url_pwd))
 
        if response.status_code == 200:
            json = response.json()  
            print("JSON data received:")
            return json
        else:
            print(f"❌ Request failed with status code {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
 
 
 
def main() -> None:
    """
    Main method. Actions summary:
    1. Check for new overlays in the last 2 days
    2. Load overlay data to the database
    """
 
    print("Starting ImageOverlay")
    json = get_overlay_list()
    print(json)
    connection = oracledb.connect(user=args.user, password=args.password, dsn=args.dsn)
    print("✅ Connected to Oracle Database")
 
if __name__ == "__main__":
    main()