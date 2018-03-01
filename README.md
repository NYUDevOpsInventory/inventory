[![Build Status](https://travis-ci.org/NYUDevOpsInventory/inventory.svg?branch=master)](https://travis-ci.org/NYUDevOpsInventory/inventory)

# Inventory Team


Paths:
------
GET /
- Returns useful information about the service.

GET /inventory
- Returns all the product information in the Inventory.

GET /inventory/{prod_id}
- Returns production information about a certain product.

POST /inventory
- Adds a new product with its information to the inventory.

PUT /inventory/{prod_id}
- Updates information of a product.

DELETE /inventory/{prod_id}
- Deletes product information with the given product id.

GET /inventory?{prod_name|quantity|condition=val}
- Returns all products' information meeting given requirement.

PUT /inventory/{prod_id}/restock
- An action triggers restocking for a product.