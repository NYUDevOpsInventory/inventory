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

# import threading
from flask_sqlalchemy import SQLAlchemy

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

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

db = SQLAlchemy()

class ProductInformation(db.Model):
    """ A class representing an Inventory entry"""

    app = None

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
        if (data_new_qty is not None and data_new_qty < DEFAULT_NEW_QTY) or \
                (data_used_qty is not None and data_used_qty < DEFAULT_USED_QTY) or \
                (data_open_boxed_qty is not None and data_open_boxed_qty < DEFAULT_OPEN_BOXED_QTY) \
                or \
                (data_restock_level is not None and data_restock_level < DEFAULT_RESTOCK_LEVEL) or \
                (data_restock_amt is not None and data_restock_amt < DEFALUT_RESTOCK_AMT):
            raise DataValidationError(BAD_DATA_MSG)
        
        # populate ProductInformation with given data or None
        self.new_qty = data_new_qty
        self.used_qty = data_used_qty
        self.open_boxed_qty = data_open_boxed_qty
        self.restock_level = data_restock_level
        self.restock_amt = data_restock_amt

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

    @staticmethod
    def init_db(app):
        """ Initialize database """
        ProductInformation.app = app
        db.init_app(app)
        app.app_context().push()
        db.create_all()

    @staticmethod
    def find(prod_id):
        """ Find an ProductInformation by the prod_id """
        return ProductInformation.query.get(prod_id)

    @staticmethod
    def list_all():
        """ Returns all ProductInformation in the database """
        return ProductInformation.query.all()
