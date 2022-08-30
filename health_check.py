from datetime import datetime, timezone
import secrets
import string
import hashlib
import requests
from time import sleep

import logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

keyID = "REPLACE WITH API KEY ID"
keyValue = "REPLACE WITH API KEY VALUE"
tenantURL = "REPLACE WITH TENANTNAME.XDR.REGION.PALOALTONETWORKS.COM" # e.g. test.xdr.uk.paloaltonetworks.com

def initiate_query(api_key_id, api_key, query=""):
    if query == "":
        query = "dataset = panw_ngfw_traffic_raw"
    logging.info(f"Creating query: {query} on customer {tenantURL}")
    nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
    timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
    auth_key = "%s%s%s" % (api_key, nonce, timestamp)
    auth_key = auth_key.encode("utf-8")
    api_key_hash = hashlib.sha256(auth_key).hexdigest()
    headers = {
        "x-xdr-timestamp": str(timestamp),
        "x-xdr-nonce": nonce,
        "x-xdr-auth-id": str(api_key_id),
        "Authorization": api_key_hash,
        "Content-Type": "application/json"
    }
    parameters = {
        "request_data": {
            "query": query
        }
    }
    res = requests.post(url="https://api-"+tenantURL+"/public_api/v1/xql/start_xql_query/",
						headers=headers,
						json=parameters)
    if res.status_code == 200:
        return res.json(), query
    return "error getting incidents", query

def get_query(api_key_id, api_key, query_id):
    logging.info(f"Checking output of query ID : {query_id}")
    nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
    timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
    auth_key = "%s%s%s" % (api_key, nonce, timestamp)
    auth_key = auth_key.encode("utf-8")
    api_key_hash = hashlib.sha256(auth_key).hexdigest()
    headers = {
        "x-xdr-timestamp": str(timestamp),
        "x-xdr-nonce": nonce,
        "x-xdr-auth-id": str(api_key_id),
        "Authorization": api_key_hash,
        "Content-Type": "application/json"
    }
    parameters = {
        "request_data": {
            "query_id": query_id
        }
    }
    res = requests.post(url="https://api-"+tenantURL+"/public_api/v1/xql/get_query_results/",
						headers=headers,
						json=parameters)
    if res.status_code == 200:
        return res.json()
    return res.text

rawJson, query = initiate_query(keyID, keyValue, "dataset = check_point_vpn_1_firewall_1_raw") # replace dataset = with desired dataset to monitor

while True:
    qryId = rawJson.get('reply')
    max_wait = 60
    state = False
    for interval in range(10, max_wait, 10):
        sleep(interval)
        outputQuery = get_query(keyID, keyValue, qryId)
        if "status" in outputQuery.get("reply"):
            logging.info(f"Query status: {outputQuery['reply']['status']}")
            if outputQuery["reply"]['status'] == "SUCCESS":
                state = True
                break

    if not state:
        logging.error("Query took too long")
        exit(0)

    numResults = outputQuery['reply']['number_of_results']
    if numResults != 0:
        logging.info(f"Success, got number of results :  {numResults}")
    else:
        logging.error(f"Logging failed for query! {query} , number of results found: {numResults}")
    logging.info("Sleeping for 2 days")
    sleep(172800)
