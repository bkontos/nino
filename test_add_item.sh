#!/bin/bash

# Define the URL of your Flask application
URL="http://localhost:5000/inventory"

# JSON payload
PAYLOAD='{
  "description": "T-shirt",
  "size": "L",
  "price": 19.99,
  "count_in": 100,
  "count_out": 0,
  "comps": 0,
  "item_type": "Soft"
}'

read -p "Enter the access token: " TOKEN

# Send POST request to the Flask application
curl -X POST $URL \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d "$PAYLOAD"
