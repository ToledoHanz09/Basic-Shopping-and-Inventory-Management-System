from collections import deque
import time
import re

order_queue = deque()
accounts = {}
inventories = {}

class InvalidPasswordError(Exception):
    pass
class InvalidShopNameError(Exception):
    pass
class InsufficientFundsError(Exception):
    pass

def validate_password(password):
    if not re.match(r'^[a-zA-Z0-9]{8,16}$', password):
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
        description = input("Enter product description (or type 'back' to go back): ")
        if description.lower() == 'back':
            return
        try:
            price = float(input("Enter product price (or type 'back' to go back): "))
            if price < 0:
                raise ValueError
        except ValueError:
            print("Invalid price. Try again.")
            continue

        inventories[shop_name][product] = {
            'quantity': inventories[shop_name].get(product, {}).get('quantity', 0) + quantity,
            'description': description,
            'price': price
        }
        print(f"Added {quantity} {product}(s) to the inventory of {shop_name}.\n")
        break

def check_inventory(username):
    shop_name = accounts[username]['shop']
    if not inventories[shop_name]:
        print("Inventory is empty.\n")
        return
    print(f"\nCurrent Inventory of {shop_name}:")
    print("{:<20} {:<10} {:<20} {:<10}".format('Product', 'Quantity', 'Description', 'Price'))
    print("-" * 60)
    for product, details in inventories[shop_name].items():
        print("{:<20} {:<10} {:<20} â‚±{:<10.2f}".format(product, details['quantity'], details['description'], details['price']))
    print()

def display_available_products():
    for shop_name, inventory in inventories.items():
        if inventory:
            print(f"\nAvailable Products at {shop_name}:")
            print("{:<20} {:<10} {:<20} {:<10}".format('Product', 'Quantity', 'Description', 'Price'))
            print("-" * 60)
            for product, details in inventory.items():
                if details['quantity'] > 0:
                    print("{:<20} {:<10} {:<20} â‚±{:<10.2f}".format(product, details['quantity'], details['description'], details['price']))
    if not inventories:
        print("No products available.")

def select_shop():
    print("\nAvailable Shops:")
    for shop in inventories.keys():
        print(shop)
    while True:
        shop_name = input("Select a shop (or type 'back' to go back): ")
        if shop_name.lower() == 'back':
            return None
        if shop_name in inventories:
            print(f"\nProducts available at {shop_name}:")
            print("{:<20} {:<10} {:<20} {:<10}".format('Product', 'Quantity', 'Description', 'Price'))
            print("-" * 60)
            for product, details in inventories[shop_name].items():
                print("{:<20} {:<10} {:<20} â‚±{:<10.2f}".format(product, details['quantity'], details['description'], details['price']))
            return shop_name
        else:
            print("Shop not found. Try again.")

class OrderSystem:
    def check_out_order(self, username):
        while True:
            shop_name = select_shop()
            if not shop_name:
                return
            if not inventories[shop_name]:
                print(f"{shop_name} has no products available.")
                continue

            product = input("Product (or type 'back' to go back): ")
            if product.lower() == 'back':
                return
            if product not in inventories[shop_name]:
                print("Product not available. Try again.")
                continue

            try:
                quantity = int(input("Quantity (or type 'back' to go back): "))
                if quantity == 'back':
                    return
                if quantity <= 0 or quantity > inventories[shop_name][product]['quantity']:
                    raise ValueError

            except ValueError:
                print("Invalid quantity. Try again.")
                continue

            address = input("Address (or type 'back' to go back): ")
            if address.lower() == 'back':
                return

            if not address:
                print("Address can't be empty. Try again.")
                continue

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
            inventories[shop_name][product]['quantity'] -= quantity
            print(f"Order for {quantity} {product}(s) from {shop_name} placed by {username} at {address} has been added.\n")
            break

    def deliver_order(self, username):
        user_orders = [order for order in order_queue if order['Name'] == username]
        if user_orders:
            delivered_order = user_orders[0]
            order_queue.remove(delivered_order)
            total_price = delivered_order['Total']
            print(f"Delivering {delivered_order['Name']}'s order from {delivered_order['Shop']} at {delivered_order['Address']}...")
            print(f"Total price: â‚±{total_price:.2f}")

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
            print(f"Change: â‚±{change:.2f}")
        else:
            print("No orders to deliver.\n")

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
            print("C. Cancel Order")
            print("D. Display Orders")
            print("E. Log Out")
            print("F. Switch Account")
            print("G. Exit")
        else:
            print("\nA. Add Stock")
            print("B. Check Inventory")
            print("C. Log Out")
            print("D. Switch Account")
            print("E. Exit")

        user_input = input("Choose one of the following (or type 'back' to go back): ").casefold()

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
                try:
                    position = input("Choose an order to cancel (num) (or type 'back' to go back): ")
                    if position.lower() == 'back':
                        continue
                    position = int(position)
                    if position:
                        order_system.cancel_order(position)
                except ValueError:
                    print("Invalid input.")
            else:
                current_user = log_out()
        elif user_input == 'd':
            if role == 'user':
                order_system.display_orders()
            else:
                current_user = switch_account()
        elif user_input == 'e':
            if role == 'user':
                current_user = log_out()
            else:
                print("Exiting program...")
                time.sleep(2)
                break
        elif user_input == 'f' and role == 'user':
            current_user = switch_account()
        elif user_input == 'g' and role == 'user':
            print("Exiting program...")
            time.sleep(2)
            break
        else:
            print("Invalid choice. Try again.")
