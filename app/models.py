"""
Models for Inventory Management Service

All of the models are stored in this module

Models
------
ProductInformation - An Inventory entry used in the service

Attributes:
-----------
prod_id         (int)       - the id of the product
prod_name       (string)    - the name of the product
new_qty         (int)       - quantity of the new product
used_qty        (int)       - quantity of the used product
open_boxed_qty  (int)       - quantity of the open-boxed product
restock_level   (int)       - when the product total quantity reaches below this number,
                              an automatic restock will be trigger.
restock_amt     (int)       - the amount of new products restocked
                              when the total quantity goes under restock_level
"""

import logging
import math
from . import db

# Default ProductInformation property value
DEFAULT_NEW_QTY = 0
DEFAULT_USED_QTY = 0
DEFAULT_OPEN_BOXED_QTY = 0
DEFAULT_RESTOCK_LEVEL = -1  # -1 means the product won't restock automatically
DEFALUT_RESTOCK_AMT = 0

PROD_ID = 'prod_id'
PROD_NAME = 'prod_name'
NEW_QTY = 'new_qty'
USED_QTY = 'used_qty'
OPEN_BOXED_QTY = 'open_boxed_qty'
RESTOCK_LEVEL = 'restock_level'
RESTOCK_AMT = 'restock_amt'

BAD_DATA_MSG = 'Invalid ProductInformation: body of request contained bad or no data'
BAD_PARAMETER_MSG = 'Invalid parameters in the request'
RESTOCK_FAIL_MSG = 'Automatic restocking failed due to invalid ProductInformation.'

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class ProductInformation(db.Model):
    """ A class representing an Inventory entry"""
    logger = logging.getLogger(__name__)

    # Table Schema
    prod_id = db.Column(db.Integer, primary_key=True)
    prod_name = db.Column(db.String(80))
    new_qty = db.Column(db.Integer)
    used_qty = db.Column(db.Integer)
    open_boxed_qty = db.Column(db.Integer)
    restock_level = db.Column(db.Integer)
    restock_amt = db.Column(db.Integer)

    def __repr__(self):
        return repr(self.serialize())

    def save(self):
        """
        Saves an ProductInformation to database,
        currently no duplicate detection is supported.
        """
        if self.restock_level is not None and self.restock_level > 0:
            self.automatic_restock()

        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete an ProductInformation from database.
        """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """
        Serialize an ProductInformation into a dictionary.
        """
        return {
            PROD_ID: self.prod_id,
            PROD_NAME: self.prod_name,
            NEW_QTY: self.new_qty,
            USED_QTY: self.used_qty,
            OPEN_BOXED_QTY: self.open_boxed_qty,
            RESTOCK_LEVEL: self.restock_level,
            RESTOCK_AMT: self.restock_amt
        }

    def deserialize(self, data, initialize_property=True):
        """
        Deserializes an ProductInformation from a dictionary.

        Args:
            data (dict): A dictionary containing the ProductInformation data
            initialize_property (bool): A boolean indicating whether to
                initialize the ProductInformation properties to default value.
        """
        if not isinstance(data, dict):
            raise DataValidationError(BAD_DATA_MSG)
        # only prod_id & prod_name is a must-have property
        try:
            self.prod_id = data[PROD_ID]
            self.prod_name = data[PROD_NAME]
        except KeyError as error:
            raise DataValidationError('Invalid ProductInformation: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError(BAD_DATA_MSG)

        data_new_qty = data.get(NEW_QTY)
        data_used_qty = data.get(USED_QTY)
        data_open_boxed_qty = data.get(OPEN_BOXED_QTY)
        data_restock_level = data.get(RESTOCK_LEVEL)
        data_restock_amt = data.get(RESTOCK_AMT)

        # Ensure optional fields are not smaller than default values.
        if (data_new_qty is not None and data_new_qty < 0) or \
                (data_used_qty is not None and data_used_qty < 0) or \
                (data_open_boxed_qty is not None and data_open_boxed_qty < 0) or \
                (data_restock_level is not None and data_restock_level < DEFAULT_RESTOCK_LEVEL) or \
                (data_restock_amt is not None and data_restock_amt < 0):
            raise DataValidationError(BAD_DATA_MSG)

        # populate ProductInformation with given data or None
        self.new_qty = int(data_new_qty) if data_new_qty else None
        self.used_qty = int(data_used_qty) if data_used_qty else None
        self.open_boxed_qty = int(data_open_boxed_qty) if data_open_boxed_qty else None
        self.restock_level = int(data_restock_level) if data_restock_level else None
        self.restock_amt = int(data_restock_amt) if data_restock_amt else None

        if initialize_property:
            if self.new_qty is None:
                self.new_qty = DEFAULT_NEW_QTY
            if self.used_qty is None:
                self.used_qty = DEFAULT_USED_QTY
            if self.open_boxed_qty is None:
                self.open_boxed_qty = DEFAULT_OPEN_BOXED_QTY
            if self.restock_level is None:
                self.restock_level = DEFAULT_RESTOCK_LEVEL
            if self.restock_amt is None:
                self.restock_amt = DEFALUT_RESTOCK_AMT

        return self

    def restock(self, amt):
        """
        Add 'amt' of products to this ProductInfo's new_qty.
        Created for manual restock action.
        """
        if self.new_qty is None:
            raise DataValidationError(BAD_DATA_MSG)
        self.new_qty += amt
        return self

    def automatic_restock(self):
        """
        Adds new products if product quantity drops below 'restock_level'
        until the total product quantity has reached 'restock_amt',
        assuming all related properties of ProductInformation are initialized (i.e. not None).
        """
        if self.new_qty is None or self.used_qty is None or self.open_boxed_qty is None or \
                self.restock_level is None or self.restock_amt is None:
            raise DataValidationError(RESTOCK_FAIL_MSG)

        total_qty = self.new_qty + self.used_qty + self.open_boxed_qty
        if total_qty < self.restock_level:
            self.new_qty += self.restock_amt * \
                    math.ceil((self.restock_level - total_qty) / float(self.restock_amt))
        return self

    def deserialize_update(self, data):
        """
        Deserializes an ProductInformation from a dictionary.

        Args:
            data (dict): A dictionary containing the ProductInformation data
        """
        if not isinstance(data, dict):
            raise DataValidationError(BAD_DATA_MSG)
        #retrive all the data
        data_prod_id = data.get(PROD_ID)
        if data_prod_id is not None:
            raise DataValidationError(BAD_DATA_MSG)
        data_prod_name = data.get(PROD_NAME)
        data_new_qty = data.get(NEW_QTY)
        data_used_qty = data.get(USED_QTY)
        data_open_boxed_qty = data.get(OPEN_BOXED_QTY)
        data_restock_level = data.get(RESTOCK_LEVEL)
        data_restock_amt = data.get(RESTOCK_AMT)

        # Ensure optional fields are not smaller than default values.
        if (data_new_qty is not None and data_new_qty < 0) or \
                (data_used_qty is not None and data_used_qty < 0) or \
                (data_open_boxed_qty is not None and data_open_boxed_qty < 0) \
                or \
                (data_restock_level is not None and data_restock_level < DEFAULT_RESTOCK_LEVEL) or \
                (data_restock_amt is not None and data_restock_amt < 0):
            raise DataValidationError(BAD_DATA_MSG)

        # update ProductInformation only if necessary data is provided

        if data_prod_name is not None:
            self.prod_name = data_prod_name
        if data_new_qty is not None:
            self.new_qty = int(data_new_qty)
        if data_used_qty is not None:
            self.used_qty = int(data_used_qty)
        if data_open_boxed_qty is not None:
            self.open_boxed_qty = int(data_open_boxed_qty)
        if data_restock_level is not None:
            self.restock_level = int(data_restock_level)
        if data_restock_amt is not None:
            self.restock_amt = int(data_restock_amt)

        return self

    @staticmethod
    def init_db():
        """ Initialize database """
        ProductInformation.logger.info('Initializing database')
        db.create_all()

    @staticmethod
    def find(prod_id):
        """ Find an ProductInformation by the prod_id """
        return ProductInformation.query.get(prod_id)

    @staticmethod
    def find_by_name(name):
        """ Returns all inventories with the given name

        Args:
            name (string): the name of the inventory you want to match
        """
        return ProductInformation.query.filter(ProductInformation.prod_name == name).all()

    @staticmethod
    def find_by_quantity(quantity):
        """ Returns all inventories with the given quantity

        Args:
            quantity (int): the quantity of the inventory you want to match
        """
        return ProductInformation.query.filter(
            ProductInformation.new_qty + ProductInformation.used_qty
            + ProductInformation.open_boxed_qty == quantity).all()

    @staticmethod
    def find_by_condition(condition):
        """ Returns all inventories with the given condition

        Args:
            condition (string): the condition of the inventory you want to match
        """
        if condition == "new":
            return ProductInformation.query.filter(ProductInformation.new_qty > 0).all()
        elif condition == "used":
            return ProductInformation.query.filter(ProductInformation.used_qty > 0).all()
        elif condition == "open-boxed":
            return ProductInformation.query.filter(ProductInformation.open_boxed_qty > 0).all()
        else:
            raise DataValidationError(BAD_PARAMETER_MSG)

    @staticmethod
    def list_all():
        """ Returns all ProductInformation in the database """
        return ProductInformation.query.all()
