import sqlite3
from collections import deque
import time
import re

order_queue = deque()

class InvalidPasswordError(Exception):
    pass

class InvalidShopNameError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

def validate_password(password):
    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,16}$', password):
        return
    raise InvalidPasswordError("Password must be alphanumeric and between 8 to 16 characters.")

def validate_shop_name(shop_name):
    if shop_name in inventories:
        raise InvalidShopNameError("Shop name is not available. Please choose a different shop name.")

def sign_up():
    while True:
        username = input("Enter a new username (or type 'back' to go back): ")
        if username.lower() == 'back':
            return
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
        role = input("Enter role (user/seller) (or type 'back' to go back): ").lower()
        if role == 'back':
            return
        if role in ['user', 'seller']:
            break
        else:
            print("Invalid role. Try again.")

    shop_name = None
    if role == 'seller':
        while True:
            shop_name = input("Enter your shop name (or type 'back' to go back): ")
            if shop_name.lower() == 'back':
                return
            try:
                validate_shop_name(shop_name)
                inventories[shop_name] = {}
                break
            except InvalidShopNameError as e:
                print(e)
                print("Please try again.")

    accounts[username] = {'password': password, 'role': role, 'shop': shop_name}
    save_account(username, password, role, shop_name)
    print(f"Account created for {username} as {role}.\n")

def log_in():
    while True:
        username = input("Enter your username (or type 'back' to go back): ")
        if username.lower() == 'back':
            return None
        if username not in accounts:
            print("Username not found. Try again.")
        else:
            break

    while True:
        password = input("Enter your password (or type 'back' to go back): ")
        if password.lower() == 'back':
            return None
        if accounts[username]['password'] != password:
            print("Incorrect password. Try again.")
        else:
            break

    print(f"Welcome, {username}.\n")
    return username

def log_out():
    print("You have been logged out.\n")
    return None

def switch_account():
    return log_in()

def add_stock(username):
  shop_name = accounts[username]['shop']
  while True:
    product = input("Enter product name (or type 'back' to go back): ")
    if product.lower() == 'back':
      return
    if not product:
      print("Product name can't be empty. Try again.")
      continue

    try:
      quantity = int(input("Enter quantity (or type 'back' to go back): "))
      if quantity < 0:
        raise ValueError
    except ValueError:
      print("Invalid quantity. Try again.")
      continue

    while True:
      description = input("Enter product description (or type 'back' to go back): ")
      if description.lower() == 'back':
        return
      if not description:
        print("Product description can't be empty. Try again.")
      else:
        break

    try:
      price = float(input("Enter product price (or type 'back' to go back): "))
      if price < 0:
        raise ValueError
    except ValueError:
      print("Invalid price. Try again.")
      continue

    
    if shop_name not in inventories:
      inventories[shop_name] = {}

    product_key = (product, description)
    if product_key not in inventories[shop_name]:
      inventories[shop_name][product_key] = {'quantity': 0, 'price': price}
    
    inventories[shop_name][product_key]['quantity'] += quantity
    save_inventory(shop_name, product, description, inventories[shop_name][product_key]['quantity'], price)
    print(f"Added {quantity} {product}(s) to the inventory of {shop_name}.\n")
    break


def check_inventory(username):
    shop_name = accounts[username]['shop']
    if not inventories[shop_name]:
        print("Inventory is empty.\n")
        return

    print(f"\nCurrent Inventory of {shop_name}:")
    print("{:<20} {:<20} {:<10} {:<10}".format('Product', 'Description', 'Quantity', 'Price'))
    print("-" * 70)
    for (product, description), details in inventories[shop_name].items():
        print("{:<20} {:<20} {:<10} ₱{:<10.2f}".format(product, description, details['quantity'], details['price']))
    print()

def display_available_products():
    if not inventories:
        print("No products available.")
        return

    shop_list = list(inventories.keys())
    for idx, shop_name in enumerate(shop_list):
        inventory = inventories[shop_name]
        if inventory:
            print(f"\n{idx + 1}. Available Products at {shop_name}:")
            print("{:<20} {:<20} {:<10} {:<10}".format('Product', 'Description', 'Quantity', 'Price'))
            print("-" * 70)
            for (product, description), details in inventory.items():
                if details['quantity'] > 0:
                    print("{:<20} {:<20} {:<10} ₱{:<10.2f}".format(product, description, details['quantity'], details['price']))

def select_shop():
    print("\nAvailable Shops:")
    shop_list = list(inventories.keys())
    for idx, shop_name in enumerate(shop_list):
        print(f"{idx + 1}. {shop_name}")

    while True:
        shop_index = input("Select a shop by number (or type 'back' to go back): ")
        if shop_index.lower() == 'back':
            return None
        try:
            shop_index = int(shop_index) - 1
            if 0 <= shop_index < len(shop_list):
                shop_name = shop_list[shop_index]
                print(f"\nProducts available at {shop_name}:")
                print("{:<20} {:<20} {:<10} {:<10}".format('Product', 'Description', 'Quantity', 'Price'))
                print("-" * 70)
                for (product, description), details in inventories[shop_name].items():
                    print("{:<20} {:<20} {:<10} ₱{:<10.2f}".format(product, description, details['quantity'], details['price']))
                return shop_name
            else:
                print("Invalid selection. Try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

class OrderSystem:
    def check_out_order(self, username):
        while True:  
            shop_name = select_shop()
            if not shop_name:
                return

            while True:  
                product = input("Product (or type 'back' to go back): ")
                if product.lower() == 'back':
                    break

                matching_products = [(p, d) for (p, d) in inventories[shop_name] if p == product]
                if not matching_products:
                    print("Product not available. Try again.")
                    continue

                
                if len(matching_products) > 1:
                    print(f"Multiple descriptions found for {product}:")
                    for idx, (p, d) in enumerate(matching_products):
                        print(f"{idx + 1}. {d}")
                    
                    while True:  # Loop for description selection
                        try:
                            choice = int(input("Select the description number: ")) - 1
                            if choice < 0 or choice >= len(matching_products):
                                raise ValueError
                            selected_product = matching_products[choice]
                            break  
                        except ValueError:
                            print("Invalid selection. Try again.")

                else:
                    selected_product = matching_products[0]  

                while True:  
                    try:
                        quantity_input = input("Quantity (or type 'back' to go back): ")
                        if quantity_input.lower() == 'back':
                            break  
                        quantity = int(quantity_input)  
                        if quantity <= 0 or quantity > inventories[shop_name][selected_product]['quantity']:
                            raise ValueError
                        break  
                    except ValueError:
                        print("Invalid quantity. Try again.")

                if quantity_input.lower() == 'back':  
                    continue  

                
                address = input("Address (or type 'back' to go back): ")
                if address.lower() == 'back':
                    continue  

                
                order = {
                    'Name': username,
                    'Shop': shop_name,
                    'Address': address,
                    'Product': selected_product[0],
                    'Description': selected_product[1],
                    'Quantity': quantity,
                    'Price': inventories[shop_name][selected_product]['price'],
                    'Total': quantity * inventories[shop_name][selected_product]['price']
                }
                order_queue.append(order)
                inventories[shop_name][selected_product]['quantity'] -= quantity
                print(f"Order placed: {quantity} x {product} (₱{order['Price']:.2f} each) from {shop_name}.\n")
                break

    def deliver_order(self, username):
        user_orders = [order for order in order_queue if order['Name'] == username]
        if user_orders:
            delivered_order = user_orders.pop(0)
            order_queue.remove(delivered_order)

            
            shop_name = delivered_order['Shop']
            product = delivered_order['Product']
            description = delivered_order['Description']
            quantity = delivered_order['Quantity']

            
            update_inventory_in_database(shop_name, product, description, quantity)
            

            total_price = delivered_order['Total']
            print(f"Delivering {delivered_order['Name']}'s order from {delivered_order['Shop']} at {delivered_order['Address']}...")
            print(f"Total price: ₱{total_price:.2f}")
            time.sleep(3)  
            print(f"Order Delivered: {delivered_order['Quantity']} x {delivered_order['Product']} (₱{delivered_order['Price']:.2f} each) from {delivered_order['Shop']}.\n")

            while True:
                try:
                    money = float(input("Enter your money: "))
                    if money < total_price:
                        raise InsufficientFundsError("Insufficient funds. Please provide enough money.")
                    change = money - total_price
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid amount.")
                except InsufficientFundsError as e:
                    print(e)
            
            print(f"The order of {delivered_order['Name']} from {delivered_order['Shop']} at {delivered_order['Address']} has been delivered.\n")
            print(f"Change: ₱{change:.2f}")

            
            product_key = (product, description)
            if inventories[shop_name][product_key]['quantity'] <= 0:
                inventories[shop_name].pop(product_key)
                delete_product_from_database(shop_name, product, description)
        else:
            print("No orders to deliver.\n")

    def cancel_order(self, username):
        user_orders = [order for order in order_queue if order['Name'] == username]
        if user_orders:
            print("\nYour Orders:")
            for i, order in enumerate(user_orders):
                print(f"{i+1}. {order['Product']} ({order['Quantity']}) from {order['Shop']}")

            while True:
                try:
                    choice = int(input("Enter the number of the order you want to cancel (or 0 to go back): "))
                    if choice == 0:
                        return  
                    if 1 <= choice <= len(user_orders):
                        canceled_order = user_orders[choice-1]  
                        break  
                    else:
                        raise ValueError  
                except ValueError:
                    print("Invalid choice. Please enter a valid number.")

            order_queue.remove(canceled_order)
            inventories[canceled_order['Shop']][(canceled_order['Product'], canceled_order['Description'])]['quantity'] += canceled_order['Quantity']
            print(f"Order for {canceled_order['Product']} ({canceled_order['Quantity']}) from {canceled_order['Shop']} has been canceled.\n")

        else:
            print("No orders to cancel.\n")

    def display_orders(self, username):
        user_orders = [order for order in order_queue if order['Name'] == username]
        if user_orders:
            print(f"\nOrders for {username}:")
            print("{:<20} {:<20} {:<10} {:<10} {:<10}".format('Shop', 'Product', 'Description', 'Quantity', 'Total'))
            print("-" * 70)
            for order in user_orders:
                print("{:<20} {:<20} {:<10} {:<10} ₱{:<10.2f}".format(
                    order['Shop'], order['Product'], order['Description'], order['Quantity'], order['Total']
                ))
        else:
            print("No orders to display.\n")

def initialize_database():
    global conn  
    try:
        conn = sqlite3.connect('shop_system.db')
        c = conn.cursor()        
        c.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                shop_name TEXT NOT NULL,
                address TEXT NOT NULL,
                product TEXT NOT NULL,
                description TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while initializing the database: {e}")

def load_data():
    conn = sqlite3.connect('shop_system.db')
    c = conn.cursor()

    c.execute('SELECT * FROM accounts')
    for row in c.fetchall():
        username, password, role, shop_name = row
        accounts[username] = {'password': password, 'role': role, 'shop': shop_name}

    c.execute('SELECT * FROM inventories')
    for row in c.fetchall():
        shop_name, product, description, quantity, price = row
        if shop_name not in inventories:
            inventories[shop_name] = {}
        inventories[shop_name][(product, description)] = {'quantity': quantity, 'price': price}

    conn.close()

def save_account(username, password, role, shop_name):
    try:
        c = conn.cursor() 
        c.execute('''
            INSERT OR REPLACE INTO accounts (username, password, role, shop_name)
            VALUES (?, ?, ?, ?)
        ''', (username, password, role, shop_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while saving account data: {e}")

def save_inventory(shop_name, product, description, quantity, price):
    try:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO inventories (shop_name, product, description, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (shop_name, product, description, quantity, price))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while saving inventory data: {e}")


def add_static_shops():
    static_shops = {
        'Foods': [
            ('Apple', 'Fresh red apple', 100, 13.50),
            ('Banana', 'Yellow banana', 150, 14.50),
            ('Orange', 'Juicy orange', 120, 18.75),
            ('Bread', 'Whole wheat bread', 80, 105.00),
            ('Milk', '1L fresh milk', 60, 120.20),
            ('Eggs', 'Dozen eggs', 90, 120.50),
            ('Chicken', '1kg chicken breast', 50, 336.00),
            ('Rice', '1kg white rice', 200, 60.00),
            ('Carrot', 'Fresh carrots', 100, 36.80),
            ('Potato', 'Brown potatoes', 120, 45.90)
        ],
        'Goods': [
            ('Shampoo', '500ml bottle', 100, 160.50),
            ('Soap', '100g bar soap', 200, 64.00),
            ('Toothpaste', '200g tube', 150, 69.50),
            ('Notebook', '200-page notebook', 80, 47.75),
            ('Pen', 'Ballpoint pen', 200, 10.50),
            ('T-shirt', 'Cotton T-shirt', 100, 200.00),
            ('Detergent', '1kg detergent powder', 90, 215.00),
            ('Coffee', '200g instant coffee', 60, 70.00),
            ('Tea', '100g black tea', 70, 80.50),
            ('Sugar', '1kg white sugar', 150, 136.50)
        ]
    }

    for shop_name, products in static_shops.items():
        inventories[shop_name] = {}
        for product, description, quantity, price in products:
            inventories[shop_name][(product, description)] = {'quantity': quantity, 'price': price}
            save_inventory(shop_name, product, description, quantity, price)

def update_inventory_in_database(shop_name, product, description, quantity):
    try:
        c = conn.cursor()
        c.execute('''
            UPDATE inventories 
            SET quantity = quantity - ?
            WHERE shop_name = ? AND product = ? AND description = ?
        ''', (quantity, shop_name, product, description))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while updating inventory in the database: {e}")

def delete_product_from_database(shop_name, product, description):  
    try:
        c = conn.cursor()
        c.execute('''
            DELETE FROM inventories 
            WHERE shop_name = ? AND product = ? AND description = ?
        ''', (shop_name, product, description))
        conn.commit()
        print(f"Removed {product} ({description}) from {shop_name}'s inventory in the database.\n")
    except sqlite3.Error as e:
        print(f"An error occurred while deleting product from database: {e}")
        
accounts = {}  
inventories = {}
conn = None

initialize_database()

try:
    load_data()
    add_static_shops()
except sqlite3.Error as e:
    print(f"Error loading data: {e}")
    exit(1)  

order_system = OrderSystem()
current_user = None


while True:
    if current_user:            
        print(f"Logged in as: {current_user}")
        print("1. Log out")
        print("2. Switch account")
        if accounts[current_user]['role'] == 'user':
            print("3. Display available products")
            print("4. Check out order")
            print("5. Deliver order")
            print("6. Cancel order")
            print("7. Display orders")
        elif accounts[current_user]['role'] == 'seller':
            print("3. Add stock")
            print("4. Check inventory")
        print("0. Exit")
    else:
        print("--Welcome to Carhins Basic Shopping and Inventory Management System--")
        print("1. Sign up")
        print("2. Log in")
        print("0. Exit")

    choice = input("Choose an option: ")

    if choice == '1':
        if current_user:
            current_user = log_out()
        else:
            sign_up()
    elif choice == '2':
        if current_user:
            current_user = switch_account()
        else:
            current_user = log_in()
    elif choice == '3' and current_user:
        if accounts[current_user]['role'] == 'user':
            display_available_products()
        elif accounts[current_user]['role'] == 'seller':
            add_stock(current_user)
    elif choice == '4' and current_user:
        if accounts[current_user]['role'] == 'user':
            order_system.check_out_order(current_user)
        elif accounts[current_user]['role'] == 'seller':
            check_inventory(current_user)
    elif choice == '5' and current_user and accounts[current_user]['role'] == 'user':
        order_system.deliver_order(current_user)
    elif choice == '6' and current_user and accounts[current_user]['role'] == 'user':
        order_system.cancel_order(current_user)
    elif choice == '7' and current_user and accounts[current_user]['role'] == 'user':
        order_system.display_orders(current_user)
    elif choice == '0':
        break
    else:
        print("Invalid option. Please try again.\n")
conn.close()
