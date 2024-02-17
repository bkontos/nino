#!/bin/bash

URL="http://localhost:5000/inventory/save_all"

read -r -d '' PAYLOAD <<EOF
{
  "items": [
    {
      "item_id": 9,
      "description": "Updated item description",
      "size": "M",
      "price": 20.99,
      "count_in": 100,
      "count_out": 10,
      "comps": 5,
      "item_type": "Soft"
    },
    {
      "description": "New item description",
      "size": "L",
      "price": 25.99,
      "count_in": 150,
      "count_out": 20,
      "comps": 10,
      "item_type": "Hard"
    }
  ]
}
EOF

# Make a POST request to the Flask application
curl -X POST $URL \
     -H "Content-Type: application/json" \
     -d "$PAYLOAD"
