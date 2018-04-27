"""
Inventory Steps
Steps file for inventory.feature.
"""

from os import getenv
import json
import requests
from compare import expect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = 30
BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')

@given(u'the following products in inventory')
def step_impl(context):
    """ Delete all ProductInformation and load new ones """
    inventory_url = context.base_url + '/inventory'
    # first delete all mentioned products (if exist)
    for row in context.table:
        context.resp = requests.delete(inventory_url + '/' + row['prod_id'])
        expect(context.resp.status_code).to_equal(200)

    # then create all mentioned products
    headers = {'Content-Type': 'application/json'}
    for row in context.table:
        data = {
            "prod_id":          int(row['prod_id']),
            "prod_name":        row['prod_name'],
            "new_qty":          int(row['new_qty']),
            "used_qty":         int(row['used_qty']),
            "open_boxed_qty":   int(row['open_boxed_qty']),
            "restock_level":    int(row['restock_level']),
            "restock_amt":      int(row['restock_amt']),
        }
        payload = json.dumps(data)
        context.resp = requests.post(inventory_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@when(u'I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@when(u'I set the "{element_id}" to "{text_string}"')
def step_impl(context, element_id, text_string):
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when(u'I press the "{button}" Button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{text_string}" in the "{element_id}" field')
def step_impl(context, text_string, element_id):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

@then(u'I should see the message "{message}"')
def step_impl(context, message):
    #element = context.driver.find_element_by_id('flash_message')
    #expect(element.text).to_contain(message)
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)
