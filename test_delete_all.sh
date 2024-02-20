#!/bin/bash

# Define the URL of your Flask application
URL="http://localhost:5000/inventory/delete_all"

read -p "Input access token " TOKEN

# Send POST request to the Flask application
curl -X DELETE $URL \
     -H "Authorization: Bearer $TOKEN"
