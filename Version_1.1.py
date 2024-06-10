from collections import deque
import time
import re

# Initialize the order queue and dictionaries for accounts and inventories
order_queue = deque()
accounts = {}
inventories = {
    "Foods": {
        "Apple": {'quantity': 10},
        "Banana": {'quantity': 10},
        "Orange": {'quantity': 10},
        "Grapes": {'quantity': 10},
        "Strawberry": {'quantity': 10},
        "Watermelon": {'quantity': 10},
        "Peach": {'quantity': 10},
        "Mango": {'quantity': 10},
        "Blueberry": {'quantity': 10},
        "Pineapple": {'quantity': 10}
    },
    "Goods": {
        "Notebook": {'quantity': 10},
        "Pen": {'quantity': 10},
        "Pencil": {'quantity': 10},
        "Eraser": {'quantity': 10},
        "Ruler": {'quantity': 10},
        "Backpack": {'quantity': 10},
        "Binder": {'quantity': 10},
        "Calculator": {'quantity': 10},
        "Folder": {'quantity': 10},
        "Markers": {'quantity': 10}
    }
}

# Custom exceptions for various error conditions
class InvalidPasswordError(Exception):
    pass

class InvalidShopNameError(Exception):
    pass

class InsufficientStockError(Exception):
    pass

class InvalidQuantityError(Exception):
    pass

# Function to validate password format
def validate_password(password):
    if not re.match(r'^[a-zA-Z0-9]{8,16}$', password):
        raise InvalidPasswordError("Password must be alphanumeric and between 8 to 16 characters.")

# Function to check shop name availability
def validate_shop_name(shop_name):
    if shop_name in inventories:
        raise InvalidShopNameError("Shop name is not available. Please choose a different shop name.")

# Function to handle user sign-up
def sign_up():
    while True:
        username = input("Enter a new username: ")
        if username in accounts:
            print("Username already exists. Try again.")
        else:
            break
    while True:
        password = input("Enter a password: ")
        try:
            validate_password(password)
            break
        except InvalidPasswordError as e:
            print(e)
            print("Please try again.")
    while True:
        role = input("Enter role (user/seller): ").lower()
        if role in ['user', 'seller']:
            break
        else:
            print("Invalid role. Try again.")

    shop_name = None
    if role == 'seller':
        while True:
            shop_name = input("Enter your shop name: ")
            try:
                validate_shop_name(shop_name)
                inventories[shop_name] = {}  # Initialize shop inventory
                break
            except InvalidShopNameError as e:
                print(e)
                print("Please try again.")

    accounts[username] = {'password': password, 'role': role, 'shop': shop_name}
    print(f"Account created for {username} as {role}.\n")

# Function to handle user login
def log_in():
    while True:
        username = input("Enter your username: ")
        if username not in accounts:
            print("Username not found. Try again.")
        else:
            break

    while True:
        password = input("Enter your password: ")
        if accounts[username]['password'] != password:
            print("Incorrect password. Try again.")
        else:
            break

    print(f"Welcome, {username}.\n")
    return username

# Function for sellers to add stock
def add_stock(username):
    shop_name = accounts[username]['shop']
    
    product = input("Enter product name: ")
    while not product:
        print("Product name can't be empty. Try again.")
        product = input("Enter product name: ")

    if product in inventories[shop_name]:
        print(f"{product} is already in the inventory. Updating quantity.")
    else:
        inventories[shop_name][product] = {'quantity': 0}
        
    while True:
        try:
            quantity = input("Enter quantity: ")
            if not quantity.isdigit():
                raise InvalidQuantityError("Invalid input. Quantity must be a number.")
            quantity = int(quantity)
            inventories[shop_name][product]['quantity'] += quantity
            break
        except InvalidQuantityError as e:
            print(e)
            print("Please try again.")

    print(f"{product} successfully added to the inventory.")

# Function to check the inventory of a seller
def check_inventory(username):
    shop_name = accounts[username]['shop']
    if not inventories[shop_name]:
        print("Inventory is empty.\n")
        return
    print(f"\nCurrent Inventory of {shop_name}:")
    print("{:<20} {:<10}".format('Product', 'Quantity'))
    print("-" * 30)
    for product, details in inventories[shop_name].items():
        print("{:<20} {:<10}".format(product, details['quantity']))

# Function to display all available products across shops
def display_available_products():
    for shop_name, inventory in inventories.items():
        if inventory:
            print(f"\nAvailable Products at {shop_name}:")
            print("{:<20} {:<10}".format('Product', 'Quantity'))
            print("-" * 30)
            for product, details in inventory.items():
                if details['quantity'] > 0:
                    print("{:<20} {:<10}".format(product, details['quantity']))
    if not inventories:
        print("No products available.")

# Function to select a shop for placing orders
def select_shop():
    print("\nAvailable Shops:")
    for shop in inventories.keys():
        print(shop)
    while True:
        shop_name = input("Select a shop: ")
        if shop_name in inventories:
            print(f"\nProducts available at {shop_name}:")
            print("{:<20} {:<10}".format('Product', 'Quantity'))
            print("-" * 30)
            for product, details in inventories[shop_name].items():
                print("{:<20} {:<10}".format(product, details['quantity']))
            return shop_name
        else:
            print("Shop not found. Try again.")

# Order system class to handle orders and deliveries
class OrderSystem:
    # Function to handle order checkout
    def check_out_order(self, username):
        while True:
            shop_name = select_shop()
            if not shop_name:
                return
            if not inventories[shop_name]:
                print(f"{shop_name} has no products available.")
                continue

            product = input("Product: ")

            if product not in inventories[shop_name] or inventories[shop_name][product]['quantity'] == 0:
                print("Product not available or out of stock. Try again.")
                continue

            while True:
                try:
                    quantity = input(f"Enter quantity for {product} (Available: {inventories[shop_name][product]['quantity']}): ")
                    if not quantity.isdigit():
                        raise InvalidQuantityError("Invalid input. Quantity must be a number.")
                    quantity = int(quantity)
                    if quantity <= inventories[shop_name][product]['quantity']:
                        break
                    else:
                        print(f"Insufficient stock. Available quantity: {inventories[shop_name][product]['quantity']}. Try again.")
                except InvalidQuantityError as e:
                    print(e)

            address = input("Address: ")

            if not address:
                print("Address can't be empty. Try again.")
                continue

            inventories[shop_name][product]['quantity'] -= quantity
            order = {
                'Name': username,
                'Shop': shop_name,
                'Address': address,
                'Product': product,
                'Quantity': quantity
            }

            order_queue.append(order)  # Add order to the queue
            print(f"Order for {quantity} {product}(s) from {shop_name} placed by {username} at {address} has been added.\n")
            break

    # Function to handle order delivery
    def deliver_order(self, username):
        user_orders = [order for order in order_queue if order['Name'] == username]
        if user_orders:
            delivered_order = user_orders[0]
            order_queue.remove(delivered_order)
            print(f"Delivering {delivered_order['Name']}'s order of {delivered_order['Quantity']} {delivered_order['Product']}(s) from {delivered_order['Shop']} at {delivered_order['Address']}...")
            print(f"The order of {delivered_order['Name']} from {delivered_order['Shop']} at {delivered_order['Address']} has been delivered.\n")
        else:
            print("No orders to deliver.\n")

# Main application loop
order_system = OrderSystem()
current_user = None

while True:
    if not current_user:
        print("1. Sign Up")
        print("2. Log In")
        print("3. Exit")

        choice = input("Choose an option: ")
        if choice == '1':
            sign_up()
        elif choice == '2':
            current_user = log_in()
        elif choice == '3':
            print("Exiting program...")
            time.sleep(2)
            break
        else:
            print("Invalid choice. Try again.")
    else:
        role = accounts[current_user]['role']

        if role == 'user':
            print("\nA. Check Out Order")
            print("B. Deliver Order")
            print("C. Display Available Products")
            print("D. Exit")
        else:
            print("\nA. Add Stock")
            print("B. Check Inventory")
            print("C. Exit")

        user_input = input("Choose one of the following: ").casefold()

        if user_input == 'a':
            if role == 'user':
                order_system.check_out_order(current_user)
            else:
                add_stock(current_user)
                
        elif user_input == 'b':
            if role == 'user':
                order_system.deliver_order(current_user)
            else:
                check_inventory(current_user)

        elif user_input == 'c':
            if role == 'user':
                display_available_products()
            else:
                print("Exiting program...")
                time.sleep(2)
                break
        elif user_input == 'd' and role == 'user':
            print("Exiting program...")
            time.sleep(2)
            break
        else:
            print("Invalid choice. Try again.")
