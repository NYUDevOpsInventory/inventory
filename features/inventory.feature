Feature: The Inventory service back-end
    As a Inventory owner
    I need a RESTful product management service
    So that I can keep track of all my product information

Background:
    Given the following products in inventory
        | prod_id | prod_name | new_qty | used_qty | open_boxed_qty | restock_level | restock_amt |
        |  1      | iPod      | 1       | 1        | 3              | 4             | 8           |
        |  2      | Macbook   | 2       | 2        | 2              | 5             | 9           |
        |  3      | iPhone    | 3       | 3        | 1              | 6             | 10          |

Scenario: Retrive an ProductInformation
    When I visit the "Home Page"
    And I set the "prod_id" to "2"
    And I press the "retrieve" Button
    Then I should see "2" in the "new_qty" field
    AND I should see "2" in the "used_qty" field
    AND I should see "2" in the "open_boxed_qty" field
    AND I should see "5" in the "restock_level" field
    AND I should see "9" in the "restock_amt" field

Scenario: Delete a product from Inventory
    When I visit the "Home Page"
    And I set the "prod_id" to "3"
    And I press the "delete" Button
    Then I should see the message "Product has been Deleted!"

Scenario: Create a new ProductInformation
    When I visit the "Home Page"
    And I set the "prod_id" to "4"
    And I set the "prod_name" to "StormTrooper"
    And I press the "create" Button
    Then I should see the message "Success"
