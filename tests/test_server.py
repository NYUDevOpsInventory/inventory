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

    def test_create_prod_info_BadRequestException(self):
        data = json.dumps({})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        
        data = json.dumps({PROD_ID: 1})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        data = json.dumps({PROD_NAME: 'whatsup'})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_create_prod_info_withAllFields(self):
        entryCount = self.getEntryCount()

        testProdId = 233333
        testProdName = 'nicai'
        testNewQty = 1111
        testUsedQty = 666
        testOpenQty = 2018
        testRestockLevel = 9
        testRestockAmt = 4
        data = json.dumps({PROD_ID: testProdId, PROD_NAME: testProdName,
                    NEW_QTY: testNewQty, USED_QTY: testUsedQty, OPEN_BOXED_QTY: testOpenQty,
                    RESTOCK_LEVEL: testRestockLevel, RESTOCK_AMT: testRestockAmt})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(response.headers.get(LOCATION, None) != None)
        returnJson = json.loads(response.data)
        self.assertIsNotNone(returnJson)
        self.assertFieldsEqual(returnJson, testProdId, testProdName, testNewQty, testUsedQty,
                testOpenQty, testRestockLevel, testRestockAmt)
        response = self.app.get(PATH_INVENTORY)
        data = json.loads(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(entryCount + 1, len(data))
        self.assertIn(returnJson, data)
                
    def test_create_prod_info_withMandatoryFields(self):
        entryCount = self.getEntryCount()

        testProdId = 233
        testProdName = 'bucai'
        data = json.dumps({PROD_ID: testProdId, PROD_NAME: testProdName})
        response = self.app.post(PATH_INVENTORY, data=data, content_type=JSON)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(response.headers.get(LOCATION, None) != None)
        returnJson = json.loads(response.data)
        self.assertIsNotNone(returnJson)
        self.assertFieldsEqual(returnJson, testProdId, testProdName, DEFAULT_NEW_QTY,
                DEFAULT_USED_QTY, DEFAULT_OPEN_BOXED_QTY, DEFAULT_RESTOCK_LEVEL,
                DEFALUT_RESTOCK_AMT)
        response = self.app.get(PATH_INVENTORY)
        data = json.loads(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(entryCount + 1, len(data))
        self.assertIn(returnJson, data)

######################################################################
# Utility functions
######################################################################
    def assertFieldsEqual(self, returnJson, expectProdId, expectProdName, expectNewQty,
            expectUsedQty, expectOpenQty, expectRestockLevel, expectRestockAmt):
        self.assertEqual(expectProdId, returnJson[PROD_ID])
        self.assertEqual(expectProdName, returnJson[PROD_NAME])
        self.assertEqual(expectNewQty, returnJson[NEW_QTY])
        self.assertEqual(expectUsedQty, returnJson[USED_QTY])
        self.assertEqual(expectOpenQty, returnJson[OPEN_BOXED_QTY])
        self.assertEqual(expectRestockLevel, returnJson[RESTOCK_LEVEL])
        self.assertEqual(expectRestockAmt, returnJson[RESTOCK_AMT])

    def getEntryCount(self):
        """ save the current number of product information entries """
        response = self.app.get(PATH_INVENTORY)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = json.loads(response.data)
        return len(data)

if __name__ == '__main__':
    unittest.main()
