[![Build Status](https://travis-ci.org/NYUDevOpsInventory/inventory.svg?branch=master)](https://travis-ci.org/NYUDevOpsInventory/inventory)
[![codecov](https://codecov.io/gh/NYUDevOpsInventory/inventory/branch/master/graph/badge.svg)](https://codecov.io/gh/NYUDevOpsInventory/inventory)

# Inventory Team

An Inventory service that keeps track of product id, name, quantity and status (i.e. new/used/open-boxed).

Public APIs:
------

Get root info
- Path: GET /
- Returns useful information about the service.

List all resources
- Path: GET /inventory
- Returns all the product information in the Inventory.

Get a resource
- Path: GET /inventory/{prod_id}
- Returns production information about a certain product.
- Input: An integer representing a product id.

Create a resource
- Path: POST /inventory
- Adds a new product with its information to the inventory.
- Input: a JSON file containing information of a certain product.

Update a resource
- Path: PUT /inventory/{prod_id}
- Updates information of a product.
- Input: An integer representing a product id; a JSON file containing info that is to be updated in a certain product.

Delete a resource
- Path: DELETE /inventory/{prod_id}
- Deletes product information with the given product id.
- Input: An integer representing a product id.

Query a resource
- Path: GET /inventory?{prod_name|quantity|condition=val}
- Returns all products' information meeting given requirement.

Perform manual restock action
- Path: PUT /inventory/{prod_id}/restock
- An action triggers restocking for a product.
- Input: An integer representing a product id.

How to run the service
------
1. Git clone and `cd` into this repo.
2. Start & login to the virtual machine using vagrant.
  ```
  vagrant up 
  vagrant ssh
  ```
3. Go the `/vagrant` directory and start the service.
  ```
  cd /vagrant
  python server.py
  ```

How to test the code
------
1. Git clone and `cd` into this repo.
2. Start & login to the virtual machine using vagrant.
  ```
  vagrant up 
  vagrant ssh
  ```
3. Go the `/vagrant` directory and test the code with nosetests.
  ```
  cd /vagrant
  nosetests
  ```
  The test results & coverage report should show up accordingly.
* We've also setup Travis CI so that the code is automatically built and tested.
