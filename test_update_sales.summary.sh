#!/bin/bash

# Define the URL of your Flask application
URL="http://localhost:5000/sales_summary/1"

# JSON payload
PAYLOAD=$(cat calculate_summary_output.json)

read -p "Input access token: " TOKEN

# Send POST request to the Flask application
curl -X PUT $URL \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d "$PAYLOAD"

rm calculate_summary_output.json


