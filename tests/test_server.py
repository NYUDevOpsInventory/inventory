"""
Inventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""

from flask_api import status
from mock import MagicMock, patch
from models import ProductInformation, DataValidationError, db
import json
import logging
import os
import server
import unittest

######################################################################
#  Fixed Global Variables
######################################################################
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db/test.db')
# Data table entry names
PROD_ID = 'prod_id'
PROD_NAME = 'prod_name'
NEW_QTY = 'new_qty'
USED_QTY = 'used_qty'
OPEN_BOXED_QTY = 'open_boxed_qty'
RESTOCK_LEVEL = 'restock_level'
RESTOCK_AMT = 'restock_amt'
# Default ProductInformation property value
DEFAULT_NEW_QTY = 0
DEFAULT_USED_QTY = 0
DEFAULT_OPEN_BOXED_QTY = 0
DEFAULT_RESTOCK_LEVEL = -1
DEFALUT_RESTOCK_AMT = 0
# API paths
PATH_INVENTORY = '/inventory'
PATH_INVENTORY_PROD_ID = '/inventory/{}'
# Action paths
PATH_RESTOCK = '/inventory/{}/restock'
# Content type
JSON = 'application/json'
# Location header
LOCATION = 'Location'

######################################################################
#  Test Cases
######################################################################
class TestInventoryServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        server.app.debug = False
        #server.initialize_logging(logging.INFO)
        server.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        server.init_db()
        db.drop_all()
        db.create_all()
        ProductInformation(prod_id=1, prod_name='a', new_qty=1, used_qty=1, open_boxed_qty=1,
                restock_level=10, restock_amt=10).save()
        ProductInformation(prod_id=2, prod_name='b', new_qty=2, used_qty=2, open_boxed_qty=2,
                restock_level=20, restock_amt=20).save()
        self.app = server.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_prod_info_bad_request(self):
        """ Test cases where not all mandatory fields are given. """
        data = json.dumps({})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        data = json.dumps({PROD_ID: 1})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        data = json.dumps({PROD_NAME: 'whatsup'})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        """ Test case for adding duplicate product information. """
        test_prod_id = 100
        test_prod_name = 'asdf'
        data = json.dumps({PROD_ID: test_prod_id, PROD_NAME: test_prod_name})
        self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)

        # BadRequest on adding duplicates but 200OK after adding a different record.
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        data = json.dumps({PROD_ID: 222, PROD_NAME: "zxcv"})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_create_prod_info_with_all_fields(self):
        """ Creating new product information with all fields. """
        entry_count = self.get_entry_count()

        test_prod_id = 233333
        test_prod_name = 'nicai'
        test_new_qty = 1111
        test_used_qty = 666
        test_open_qty = 2018
        test_restock_level = 9
        test_restock_amt = 4
        data = json.dumps({PROD_ID: test_prod_id, PROD_NAME: test_prod_name,
                    NEW_QTY: test_new_qty, USED_QTY: test_used_qty, OPEN_BOXED_QTY: test_open_qty,
                    RESTOCK_LEVEL: test_restock_level, RESTOCK_AMT: test_restock_amt})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(response.headers.get(LOCATION, None) != None)
        return_json = json.loads(response.data)
        self.assertIsNotNone(return_json)
        self.assert_fields_equal(return_json, test_prod_id, test_prod_name, test_new_qty,
                test_used_qty, test_open_qty, test_restock_level, test_restock_amt)
        response = self.app.get(PATH_INVENTORY)
        data = json.loads(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(entry_count + 1, len(data))
        self.assertIn(return_json, data)

    def test_create_prod_info_with_mandatory_fields(self):
        """ Creating new product information with mandatory fields given. """
        entry_count = self.get_entry_count()

        test_prod_id = 233
        test_prod_name = 'bucai'
        data = json.dumps({PROD_ID: test_prod_id, PROD_NAME: test_prod_name})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(response.headers.get(LOCATION, None) != None)
        return_json = json.loads(response.data)
        self.assertIsNotNone(return_json)
        self.assert_fields_equal(return_json, test_prod_id, test_prod_name, DEFAULT_NEW_QTY,
                DEFAULT_USED_QTY, DEFAULT_OPEN_BOXED_QTY, DEFAULT_RESTOCK_LEVEL,
                DEFALUT_RESTOCK_AMT)
        response = self.app.get(PATH_INVENTORY)
        data = json.loads(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(entry_count + 1, len(data))
        self.assertIn(return_json, data)

    def test_delete_prod_info(self):
        """ Deleting product information. """
        entry_count = self.get_entry_count()

        # Test deleting product information with existing prod_id
        test_prod_id = 1
        response = self.app.delete(PATH_INVENTORY_PROD_ID.format(test_prod_id), content_type=JSON)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(entry_count - 1, self.get_entry_count())

        # Test deleting product information with non-existing prod_id
        test_prod_id = 3
        response = self.app.delete(PATH_INVENTORY_PROD_ID.format(test_prod_id), content_type=JSON)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(entry_count - 1, self.get_entry_count())

    def test_list_all_prod_info(self):
        """ List all product information in database. """
        response = self.app.get(PATH_INVENTORY)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.data)
        self.assertEqual(2, len(data))
        self.assert_fields_equal(data[0], 1, 'a', 1, 1, 1, 10, 10)
        self.assert_fields_equal(data[1], 2, 'b', 2, 2, 2, 20, 20)

        # should return a message when table is empty
        response = self.app.delete(PATH_INVENTORY_PROD_ID.format(1), content_type=JSON)
        response = self.app.delete(PATH_INVENTORY_PROD_ID.format(2), content_type=JSON)
        response = self.app.get(PATH_INVENTORY)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("Inventory is empty.", response.data)        

    def test_restock_action(self):
        """ Test restocking a non-existing product. """
        response = self.app.put(PATH_RESTOCK.format(3), data = json.dumps({RESTOCK_AMT: 43}),
                content_type = JSON)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        """ Test restocking an existing product information given empty input json data. """
        response = self.app.put(PATH_RESTOCK.format(1), data = json.dumps({}), content_type = JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        """ Test restocking an existing product information given input data more than restock_amt.
        """
        response = self.app.put(PATH_RESTOCK.format(1),
                data = json.dumps({PROD_NAME: "iririr", RESTOCK_AMT: 43, OPEN_BOXED_QTY: 79}), 
                content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        """ Test restocking an existing product with only restock_amt given. """
        test_prod_id = 1
        test_restock_amt = 82
        data = json.dumps({RESTOCK_AMT: test_restock_amt})
        response = self.app.put(PATH_RESTOCK.format(test_prod_id), data=data, content_type=JSON)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        return_json = json.loads(response.data)
        self.assert_fields_equal(return_json, test_prod_id, 'a', 1 + test_restock_amt, 1, 1, 10, 10)

    def test_update_prof_info(self):
        #Test updating existing prod_id
        test_prod_id = 1
        data = json.dumps({PROD_NAME :'zen',NEW_QTY :3,RESTOCK_AMT: 7})
        response = self.app.put(PATH_INVENTORY_PROD_ID.format(test_prod_id),data= data, content_type=JSON)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        new_json = json.loads(response.data)
        self.assertEqual(new_json['prod_id'],1)
        self.assertEqual(new_json['prod_name'], 'zen')
        self.assertEqual(new_json['new_qty'], 3)
        self.assertEqual(new_json['restock_amt'],7)

        #Test updating non-exisiting prod_id
        test_prod_id = 8
        data = json.dumps({PROD_NAME :'zen',NEW_QTY :3,RESTOCK_AMT : 7})
        response = self.app.put(PATH_INVENTORY_PROD_ID.format(test_prod_id),data= data, content_type=JSON)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

######################################################################
# Utility functions
######################################################################
    def assert_fields_equal(self, return_json, expect_prod_id, expect_prod_name, expect_new_qty,
            expect_used_qty, expect_open_qty, expect_restock_level, expect_restock_amt):
        self.assertEqual(expect_prod_id, return_json[PROD_ID])
        self.assertEqual(expect_prod_name, return_json[PROD_NAME])
        self.assertEqual(expect_new_qty, return_json[NEW_QTY])
        self.assertEqual(expect_used_qty, return_json[USED_QTY])
        self.assertEqual(expect_open_qty, return_json[OPEN_BOXED_QTY])
        self.assertEqual(expect_restock_level, return_json[RESTOCK_LEVEL])
        self.assertEqual(expect_restock_amt, return_json[RESTOCK_AMT])

    def get_entry_count(self):
        """ save the current number of product information entries """
        response = self.app.get(PATH_INVENTORY)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = json.loads(response.data)
        return len(data)

if __name__ == '__main__':
    unittest.main()
