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
        data = json.dumps({})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        
        data = json.dumps({PROD_ID: 1})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        data = json.dumps({PROD_NAME: 'whatsup'})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_prod_info_with_all_fields(self):
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
