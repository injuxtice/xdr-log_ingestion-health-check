# xdr-log_ingestion-health-check
continuously monitors a dataset for logs and reports if logs are at 0

The script continiously monitors the specified dataset and reports when logging is at 0. This is useful for datasets outside of PAN NGFW firewalls where monitoring of ingested data is difficult (e.g. checkpoint, Cisco ASA firewall logs etc)

Use: replace the following variables

keyID = "keyid"
keyValue = "keyvalue"
tenantURL = "tenantURL.xdr.uk.paloaltonetworks.com"

with your API credentials. For production use, replace with environment variables stored on server securely.

Useful for MSSP environment
