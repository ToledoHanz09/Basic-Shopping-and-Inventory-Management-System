from collections import deque
import re
import time

order_queue = deque()

# Custom exceptions
class InvalidPasswordError(Exception):
    pass

class InvalidShopNameError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

# Function to validate password
def validate_password(password):
    if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,16}$', password):
        return
    raise InvalidPasswordError("Password must be alphanumeric and between 8 to 16 characters.")

# Function to validate shop name
def validate_shop_name(shop_name):
    if shop_name in inventories:
        raise InvalidShopNameError("Shop name is not available. Please choose a different shop name.")

# Function to sign up
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
                inventories[shop_name] = {}
                break
            except InvalidShopNameError as e:
                print(e)
                print("Please try again.")

    accounts[username] = {'password': password, 'role': role, 'shop': shop_name}
    print(f"Account created for {username} as {role}.\n")

# Function to log in
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
    print(f"\n---------------------------------")
    print(f"Welcome, {username}.")
    return username

# Function to log out
def log_out():
    print("You have been logged out.\n")
    return None

# Main interface for the system
def main_interface():
    print("--Welcome to Carhins Basic Shopping and Inventory Management System--")
    while True:
        print("\n1. Sign Up\n2. Log In\n3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            sign_up()
        elif choice == '2':
            username = log_in()
            return username
        elif choice == '3':
            print("Exiting the system.")
            exit()
        else:
            print("Invalid choice. Try again.")

# Global dictionaries to store accounts, inventories, and balances
accounts = {}
inventories = {}
balances = {}

# Function to add stock (restricted to sellers)
def add_stock(username):
    user_info = accounts[username]
    if user_info['role'] != 'seller':
        return
    
    shop_name = user_info['shop']
    product_name = input("Enter product name: ")
    if product_name in inventories[shop_name]:
        quantity = int(input("Enter quantity to add: "))
        inventories[shop_name][product_name]['quantity'] += quantity
    else:
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))
        inventories[shop_name][product_name] = {'price': price, 'quantity': quantity}
    print(f"Stock updated for {shop_name}.\n")

# Function to check inventory (restricted to sellers)
def check_inventory(username):
    user_info = accounts[username]
    if user_info['role'] != 'seller':
        return

    shop_name = user_info['shop']
    print(f"\nCurrent inventory for {shop_name}:")
    for product, details in inventories[shop_name].items():
        print(f"  {product}: {details['quantity']} units")

# Function to display available products (for all users)
def display_available_products():
    print("Available Products:")
    for shop, inventory in inventories.items():
        print(f"\nShop: {shop}")
        for product, details in inventory.items():
            print(f"  {product}: {details['quantity']} units at ₱{details['price']} each ")

# Function to select shop
def select_shop():
    if not inventories:
        print("No shops available.")
        return None

    print("Available shops:")
    for idx, shop_name in enumerate(inventories.keys(), start=1):
        print(f"{idx}. {shop_name}")

    while True:
        try:
            choice = int(input("Select shop by number: "))
            if choice < 1 or choice > len(inventories):
                raise ValueError
            return list(inventories.keys())[choice - 1]
        except ValueError:
            print("Invalid selection. Try again.")

# Class to handle order system
class OrderSystem:
    def check_out_order(self, username):
        shop_name = select_shop()
        if not shop_name:
            return
        
        # Display available products for the selected shop
        print(f"\nAvailable products in {shop_name}:")
        for product, details in inventories[shop_name].items():
            print(f"  {product}: {details['quantity']} units at ₱{details['price']} each \n")

        product = input("Enter the product name you want to buy: ")

        if product not in inventories[shop_name]:
            print("Product not available. Returning to main menu.")
            return

        try:
            quantity = int(input("Enter the quantity you want to buy: "))
            if quantity <= 0 or quantity > inventories[shop_name][product]['quantity']:
                raise ValueError
        except ValueError:
            print("Invalid quantity. Returning to main menu.")
            return

        address = input("Enter your delivery address: ")

        order = {
            'Name': username,
            'Shop': shop_name,
            'Address': address,
            'Product': product,
            'Quantity': quantity,
            'Price': inventories[shop_name][product]['price'],
            'Total': quantity * inventories[shop_name][product]['price']
        }
        order_queue.append(order)
        print(f"\nOrder placed:\n"
              f"  {quantity} x {product} (₱{order['Price']:.2f} each) from {shop_name}\n"
              f"  Total: ₱{order['Total']:.2f}\n"
              f"  Delivery address: {address}\n")

        print("Returning to main menu.")

    def display_orders(self, username):
        user_orders = [order for order in order_queue if order['Name'] == username]
        if not user_orders:
            print("No orders found.")
            return

        print("Your Orders:")
        for idx, order in enumerate(user_orders, start=1):
            print(f"\nOrder {idx}:")
            print(f"  {order['Quantity']} x {order['Product']} at ₱{order['Price']} each")
            print(f"  Total: ₱{order['Total']:.2f}")
            print(f"  Delivery address: {order['Address']}")

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
            inventories[canceled_order['Shop']][canceled_order['Product']]['quantity'] += canceled_order['Quantity']
            print(f"Order for {canceled_order['Product']} ({canceled_order['Quantity']}) from {canceled_order['Shop']} has been canceled.\n")

        else:
            print("No orders to cancel.\n")

    def deliver_order(self, username):
        user_orders = [order for order in order_queue if order['Name'] == username]
        if user_orders:
            delivered_order = user_orders.pop(0)
            order_queue.remove(delivered_order)

            total_price = delivered_order['Total']
            print(f"Delivering {delivered_order['Name']}'s order from {delivered_order['Shop']} at {delivered_order['Address']}...")
            print(f"Total price: ₱{total_price:.2f}")

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
            print(f"Delivering order, please wait.")        
            time.sleep(2)
            print(f"The order of {delivered_order['Name']} from {delivered_order['Shop']} at {delivered_order['Address']} has been delivered.\n")
            print(f"Change: ₱{change:.2f}")
        else:
            print("No orders to deliver.\n")

# Function to add static shops and products
def add_static_shops():
    static_shops = {
        'Foods': [
            ('Apple', 100, 13.50),
            ('Banana', 150, 14.50),
            ('Orange',  120, 18.75),
            ('Bread',  80, 105.00),
            ('Milk',  60, 120.20),
            ('Eggs',  90, 120.50),
            ('Chicken',  50, 336.00),
            ('Rice',  200, 60.00),
            ('Carrot',  100, 36.80),
            ('Potato',  120, 45.90)
        ],
        'Goods': [
            ('Shampoo',  100, 160.50),
            ('Soap',  200, 64.00),
            ('Toothpaste', 150, 69.50),
            ('Notebook',  80, 47.75),
            ('Pen',  200, 10.50),
            ('T-shirt',  100, 200.00),
            ('Detergent',  90, 215.00),
            ('Coffee',  60, 70.00),
            ('Tea',  70, 80.50),
            ('Sugar', 150, 136.50)
        ]
    }

    for shop_name, products in static_shops.items():
        inventories[shop_name] = {}
        for product in products:
            name, quantity, price = product
            inventories[shop_name][name] = {'quantity': quantity, 'price': price}

# Main function
def main():
    # Add static shops and products
    add_static_shops()

    username = main_interface()
    order_system = OrderSystem()
    
    while True:
        user_role = accounts.get(username, {}).get('role')
        
        if user_role == 'seller':
            print("\n1. Log Out\n2. Add Stock\n3. Check Inventory\n4. Exit")
        else:  # user_role == 'user'
            print("\n1. Log Out\n2. Display Available Products\n3. Check Out Order\n4. Deliver Order\n5. Cancel Order\n6. Display Orders\n7. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            username = log_out()
            username = main_interface()
        elif choice == '2' and user_role == 'seller':
            add_stock(username)
        elif choice == '3' and user_role == 'seller':
            check_inventory(username)
        elif choice == '2' and user_role == 'user':
            display_available_products()
        elif choice == '3' and user_role == 'user':
            order_system.check_out_order(username)
        elif choice == '4' and user_role == 'user':
            order_system.deliver_order(username)
        elif choice == '5' and user_role == 'user':
            order_system.cancel_order(username)
        elif choice == '6' and user_role == 'user':
            order_system.display_orders(username)
        elif (choice == '4' and user_role == 'seller') or (choice == '7' and user_role == 'user'):
            print("Exiting the system.")
            exit()
        else:
            print("Invalid choice or access denied. Try again.")

# Call main function to run the system
main()
