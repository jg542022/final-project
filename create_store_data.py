import mysql.connector
from mysql.connector import Error

# Configuration - specific to your setup
class DbConfig:
    def __init__(self,
                 host="127.0.0.1",
                 port=3306,
                 user="root",
                 password="sinatra1",  # Matches the password in your main app
                 database="cs3260-project"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

def seed_data():
    cfg = DbConfig()
    conn = None
    cursor = None
    
    # SQL commands to execute
    commands = [
        "SET FOREIGN_KEY_CHECKS = 0",
        "TRUNCATE TABLE items_in_store",
        "TRUNCATE TABLE items",
        "TRUNCATE TABLE stores",
        "SET FOREIGN_KEY_CHECKS = 1",
        
        # Insert Stores
        """INSERT INTO stores (store_id, name) VALUES 
           (1, 'Tech Haven'),
           (2, 'Luxury Motors & Goods'),
           (3, 'Corner Market'),
           (4, 'The Fashion House')""",

        # Insert Items
        """INSERT INTO items (item_id, name) VALUES 
           (1, 'High-End Laptop'),
           (2, 'Smartphone Pro'),
           (3, 'Wireless Headphones'),
           (4, 'Sports Car'),
           (5, 'Gold Watch'),
           (6, 'Private Jet Rental (1 Hour)'),
           (7, 'Loaf of Bread'),
           (8, 'Gallon of Milk'),
           (9, 'Designer Handbag'),
           (10, 'Silk Scarf')""",

        # Stock Store 1: Tech Haven
        """INSERT INTO items_in_store (item_id, store_id, price, num_in_stock) VALUES 
           (1, 1, 2500, 15),
           (2, 1, 1200, 30),
           (3, 1, 300, 50)""",

        # Stock Store 2: Luxury Motors
        """INSERT INTO items_in_store (item_id, store_id, price, num_in_stock) VALUES 
           (4, 2, 85000, 3),
           (5, 2, 15000, 5),
           (6, 2, 5000, 100)""",

        # Stock Store 3: Corner Market
        """INSERT INTO items_in_store (item_id, store_id, price, num_in_stock) VALUES 
           (7, 3, 5, 100),
           (8, 3, 4, 80),
           (3, 3, 350, 5)""",

        # Stock Store 4: Fashion House
        """INSERT INTO items_in_store (item_id, store_id, price, num_in_stock) VALUES 
           (9, 4, 3500, 10),
           (10, 4, 450, 20),
           (5, 4, 15500, 2)"""
    ]

    try:
        conn = mysql.connector.connect(
            host=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password,
            database=cfg.database
        )

        if conn.is_connected():
            cursor = conn.cursor()
            print("Connected to database...")
            
            for sql in commands:
                try:
                    cursor.execute(sql)
                    print(f"Executed: {sql[:40]}...") # Print first 40 chars
                except Error as e:
                    print(f"Error executing command: {e}")
            
            conn.commit()
            print("\nSuccess! Database has been populated with stores and items.")

    except Error as e:
        print(f"Connection failed: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    seed_data()
