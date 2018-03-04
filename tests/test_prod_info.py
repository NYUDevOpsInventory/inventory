"""
Test cases for ProductInformation Model

Test cases can be run with:
    nosetests
    coverage report -m
"""

from models import db, DataValidationError, ProductInformation
from server import app
import os
import unittest

# Default ProductInformation property value
DEFAULT_NEW_QTY = 0
DEFAULT_USED_QTY = 0
DEFAULT_OPEN_BOXED_QTY = 0
DEFAULT_RESTOCK_LEVEL = -1
DEFALUT_RESTOCK_AMT = 0
# Attribute names' string
PROD_ID = 'prod_id'
PROD_NAME = 'prod_name'
NEW_QTY = 'new_qty'
USED_QTY = 'used_qty'
OPEN_BOXED_QTY = 'open_boxed_qty'
RESTOCK_LEVEL = 'restock_level'
RESTOCK_AMT = 'restock_amt'

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProductInformation(unittest.TestCase):
    """ Test Cases for ProductInformation """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        ProductInformation.init_db(app)
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_construct_prod_info(self):
        """ Construct a product information and assert it exists. """
        # Test with only mandatory fields.
        test_prod_id = 1
        test_prod_name = "asdf"
        prod_info = ProductInformation(prod_id = test_prod_id, prod_name = test_prod_name)
        self.assertIsNotNone(prod_info)
        self.assert_fields_equal(prod_info, test_prod_id, test_prod_name,
                None, None, None, None, None)

        # Test with all fields.
        test_prod_id = 10
        test_prod_name = "zxcv"
        test_new_qty = 2
        test_used_qty = 3
        test_open_boxed_qty = 4
        test_restock_level = 5
        test_restock_amt = 6

        prod_info = ProductInformation(prod_id = test_prod_id, prod_name = test_prod_name,
                new_qty = test_new_qty, used_qty = test_used_qty,
                open_boxed_qty = test_open_boxed_qty, restock_level = test_restock_level,
                restock_amt = test_restock_amt)
        self.assertIsNotNone(prod_info)
        self.assert_fields_equal(prod_info, test_prod_id, test_prod_name, test_new_qty,
                test_used_qty, test_open_boxed_qty, test_restock_level, test_restock_amt)

    def test_create_prod_info(self):
        """ Create a new prodct information and add it to the data table """
        prod_infos = ProductInformation.list_all()
        self.assertEqual(prod_infos, [])

        test_prod_id = 11
        test_prod_name = "a"
        prod_info = ProductInformation(prod_id = test_prod_id, prod_name = test_prod_name)
        prod_info.save()
        prod_infos = ProductInformation.list_all()

        self.assertEqual(1, len(prod_infos))
        self.assertIsNotNone(prod_infos[0])
        self.assert_fields_equal(prod_infos[0], test_prod_id, test_prod_name,
                None, None, None, None, None)

    def test_delete_prod_info(self):
        """ Delete a product information """
        prod_info = ProductInformation(prod_id = 110, prod_name = "qwe")
        prod_info.save()
        self.assertEqual(1, len(ProductInformation.list_all()))
        prod_info.delete()
        self.assertEqual(0, len(ProductInformation.list_all()))

    def test_deserialize_prod_info(self):
        """ Test deserialization of a product information. """
        test_prod_id = 119
        test_prod_name = "fire"
        data = {PROD_ID: test_prod_id, PROD_NAME: test_prod_name}
        prod_info = ProductInformation()
        prod_info.deserialize(data)
        self.assertIsNotNone(prod_info)
        self.assert_fields_equal(prod_info, test_prod_id, test_prod_name,
                DEFAULT_NEW_QTY, DEFAULT_USED_QTY, DEFAULT_OPEN_BOXED_QTY,
                DEFAULT_RESTOCK_LEVEL, DEFALUT_RESTOCK_AMT)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data. """
        prod_info = ProductInformation()

        # Input data is not of JSON format.
        data = "this is not a dictionary"
        self.assertRaises(DataValidationError, prod_info.deserialize, data)

        # Optional fields contain values smaller than defaults.
        prod_info = ProductInformation(prod_id = 1, prod_name = "ert", new_qty = -1, used_qty = -1, open_boxed_qty = -1, restock_level = -2, restock_amt = -1)
        self.assertRaises(DataValidationError, prod_info.deserialize, data)

    def test_deserialize_restock(self):
        prod_info = ProductInformation()

        # Test deserialize_restock() with non-dictionary format input.
        data = "this is not a dictionary."
        self.assertRaises(DataValidationError, prod_info.deserialize_restock, data)

        # Test deserialize_restock() input data when new_qty is None.
        data = {RESTOCK_AMT: 19}
        self.assertRaises(DataValidationError, prod_info.deserialize_restock, data)

        # Test deserialize_restock() with input having not only restock_amt value.
        data = {USED_QTY: 100, RESTOCK_LEVEL: 89}
        self.assertRaises(DataValidationError, prod_info.deserialize_restock, data)

        # Test deserialize_restock() when new_qty is not None but restock_amt is negative.
        test_restock_amt = -6
        test_new_qty = 3
        prod_info.new_qty = test_new_qty
        self.assertRaises(DataValidationError, prod_info.deserialize_restock,
                {RESTOCK_AMT: test_restock_amt})

        # Test deserialize_restock() when new_qty is not None.
        test_restock_amt = 68
        prod_info.deserialize_restock({RESTOCK_AMT: test_restock_amt}) 
        self.assertIsNotNone(prod_info)
        self.assert_fields_equal(prod_info,
                None, None, test_new_qty + test_restock_amt, None, None, None, None)

    def test_serialize_prod_info(self):
        test_prod_id = 911
        test_prod_name = "nebula"
        prod_info = ProductInformation(prod_id = test_prod_id, prod_name = test_prod_name)
        data = prod_info.serialize()

        self.assertIsNotNone(data)
        self.assertIn(PROD_ID, data)
        self.assertEqual(test_prod_id, data[PROD_ID])
        self.assertIn(PROD_NAME, data)
        self.assertEqual(test_prod_name, data[PROD_NAME])
        self.assertIn(NEW_QTY, data)
        self.assertIsNone(data[NEW_QTY])
        self.assertIn(USED_QTY, data)
        self.assertIsNone(data[USED_QTY])
        self.assertIn(OPEN_BOXED_QTY, data)
        self.assertIsNone(data[OPEN_BOXED_QTY])
        self.assertIn(RESTOCK_LEVEL, data)
        self.assertIsNone(data[RESTOCK_LEVEL])
        self.assertIn(RESTOCK_AMT, data)
        self.assertIsNone(data[RESTOCK_AMT])

    def test_update_prod_info(self):
        """ Update a product information. """
        test_prod_id = 111
        test_prod_name = "ab"
        prod_info = ProductInformation(prod_id = test_prod_id, prod_name = test_prod_name)
        prod_info.save()

        # update
        test_new_qty = 10
        test_used_qty = 30
        test_open_boxed_qty = 40
        test_restock_level = 20
        test_restock_amt = 66
        prod_info.new_qty = test_new_qty
        prod_info.used_qty = test_used_qty
        prod_info.open_boxed_qty = test_open_boxed_qty
        prod_info.restock_level = test_restock_level
        prod_info.restock_amt = test_restock_amt

        prod_infos = ProductInformation.list_all()
        self.assertEqual(1, len(prod_infos))
        self.assertIsNotNone(prod_infos[0])
        self.assert_fields_equal(prod_infos[0], test_prod_id, test_prod_name, test_new_qty,
                test_used_qty, test_open_boxed_qty, test_restock_level, test_restock_amt)

    def test_deserialize_update_prod_info(self):
        """ Test deserialization while updating product information. """
        #create entry in order check deserialization
        test_prod_id = 1
        test_prod_name = "asdf"
        prod_info = ProductInformation(prod_id = test_prod_id, prod_name = test_prod_name)
        self.assertIsNotNone(prod_info)
        self.assert_fields_equal(prod_info, test_prod_id, test_prod_name,
                None, None, None, None, None)

        #test deserialize_update when
        test_prod_name = "fire"
        data = {PROD_NAME: test_prod_name,RESTOCK_AMT : 5}
        prod_info.deserialize_update(data)
        self.assertIsNotNone(prod_info)
        self.assert_fields_equal(prod_info, test_prod_id, test_prod_name,
                None, None, None, None, 5)

        #test deserilaize_update when prod_id is provided
        update_prod_id = 3
        test_prod_name = "fire"
        data = {PROD_ID: update_prod_id,PROD_NAME: test_prod_name,RESTOCK_AMT : 5}
        prod_info = ProductInformation()
        self.assertRaises(DataValidationError, prod_info.deserialize_update, data)

        # Optional fields contain values smaller than defaults.
        prod_info = ProductInformation(prod_name = "ert", new_qty = -1, used_qty = -1, open_boxed_qty = -1, restock_level = -2, restock_amt = -1)
        self.assertRaises(DataValidationError, prod_info.deserialize_update, data)


######################################################################
# Utility functions
######################################################################
    def assert_fields_equal(self, prod_info, expect_prod_id, expect_prod_name, expect_new_qty,
            expect_used_qty, expect_open_boxed_qty, expect_restock_level, expect_restock_amt):
        self.assertEqual(expect_prod_id, prod_info.prod_id)
        self.assertEqual(expect_prod_name, prod_info.prod_name)
        self.assertEqual(expect_new_qty, prod_info.new_qty)
        self.assertEqual(expect_used_qty, prod_info.used_qty)
        self.assertEqual(expect_open_boxed_qty, prod_info.open_boxed_qty)
        self.assertEqual(expect_restock_level, prod_info.restock_level)
        self.assertEqual(expect_restock_amt, prod_info.restock_amt)

if __name__ == '__main__':
    unittest.main()
