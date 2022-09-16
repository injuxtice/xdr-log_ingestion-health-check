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

import argparse

parser = argparse.ArgumentParser(description="XDR health check script")
parser.add_argument("-key", "--keyvalue", help="API key value", required=True, type=str)
parser.add_argument("-keyid", help="API key ID", required=True, type=str)
parser.add_argument("-tenant", help="Tenant URL", required=True, type=str)
parser.add_argument("-query", help="Query to run", required=True, type=str)


keyID = parser.parse_args().keyid
keyValue = parser.parse_args().keyvalue
tenantURL = parser.parse_args().tenant
input_query = parser.parse_args().query

def api_call(called_parameters, input_query, api_url):
    nonce = "".join([secrets.choice(string.ascii_letters + string.digits) for _ in range(64)])
    timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
    auth_key = "%s%s%s" % (keyValue, nonce, timestamp)
    auth_key = auth_key.encode("utf-8")
    api_key_hash = hashlib.sha256(auth_key).hexdigest()
    headers = {
        "x-xdr-timestamp": str(timestamp),
        "x-xdr-nonce": nonce,
        "x-xdr-auth-id": str(keyID),
        "Authorization": api_key_hash,
        "Content-Type": "application/json"
    }
    parameters = {
        "request_data": {
            input_query: called_parameters
        }
    }
    res = requests.post(url=f"https://api-{tenantURL}/public_api/v1/xql/{api_url}",
						headers=headers,
						json=parameters)
    if res.status_code == 200:
        return res.json()
    return "error getting incidents", called_parameters

while True:
    rawJson = api_call(input_query, "query", "start_xql_query") # replace dataset = with desired dataset to monitor
    qryId = rawJson.get('reply')
    logging.info(f"Got query ID: {qryId}")
    max_wait = 60
    state = False
    for interval in range(10, max_wait, 10):
        sleep(interval)
        outputQuery = api_call(qryId, "query_id", "get_query_results")
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
        logging.error(f"Logging failed for query! , number of results found: {numResults}")
    logging.info("Sleeping for 2 days")
    sleep(172800)
