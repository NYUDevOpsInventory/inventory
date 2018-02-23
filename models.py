"""
Models for Inventory Management Service

All of the models are stored in this module

Models
------
Entry - An Inventory Entry used in the service

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

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

db = SQLAlchemy()

class Entry(db.Model):
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
        Saves an Entry to database,
        currently no duplicate detection is supported.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete an Entry from database.
        """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """
        Serialize an Entry into a dictionary.
        """
        return {
            "prod_id": self.prod_id,
            "prod_name": self.prod_name,
            "new_qty": self.new_qty,
            "used_qty": self.used_qty,
            "open_boxed_qty": self.open_boxed_qty,
            "restock_level": self.restock_level,
            "restock_amt": self.restock_amt
        }

    def deserialize(self, data, initialize_property=True):
        """
        Deserializes an Entry from a dictionary.
        Currently only prod_id is deserialized.
        Deserialization of other properties are on the way.

        Args:
            data (dict): A dictionary containing the Entry data
        """
        if not isinstance(data, dict):
            raise DataValidationError('Invalid Entry: body of request contained bad or no data')
        # only prod_id is a must-have property
        try:
            self.prod_id = data['prod_id']
        except KeyError as error:
            raise DataValidationError('Invalid Entry: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Entry: body of request contained' \
                                      'bad or no data')

        # populate Entry with data or None
        self.prod_name = data.get('prod_name')
        self.new_qty = data.get('new_qty')
        self.used_qty = data.get('used_qty')
        self.open_boxed_qty = data.get('open_boxed_qty')
        self.restock_level = data.get('restock_level')
        self.restock_amt = data.get('restock_amt')

        if initialize_property:
            if self.prod_name is None:
                self.prod_name = 'default_prod_name'
            if self.new_qty is None:
                self.new_qty = 5
            if self.used_qty is None:
                self.used_qty = 0
            if self.open_boxed_qty is None:
                self.open_boxed_qty = 0
            if self.restock_level is None:
                self.restock_level = 5
            if self.restock_amt is None:
                self.restock_amt = 20

        return self

    @staticmethod
    def init_db(app):
        """ Initialize database """
        Entry.app = app
        db.init_app(app)
        app.app_context().push()
        db.create_all()

    @staticmethod
    def list_all():
        """ Returns all Entry in the database """
        return Entry.query.all()

    @staticmethod
    def find(prod_id):
        """ Find an Entry by the prod_id """
        return Entry.query.get(prod_id)
