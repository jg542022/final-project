import mysql.connector
from mysql.connector import Error
import tkinter as tk
import tkinter.ttk as ttk
from os import system
from platform import system as platform
from datetime import date, timedelta


class PortfolioView:
    def __init__(self, frame, on_back):
        self.frame = frame

        ttk.Label(frame, text="Portfolio").pack(pady=5)

        # ---- Stock table ----
        columns = ("ticker", "shares")
        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.table.heading("ticker", text="Ticker")
        self.table.heading("shares", text="Shares")

        self.table.column("ticker", width=120)
        self.table.column("shares", width=100, anchor="e")

        self.table.pack(fill="both", expand=True, pady=10)

        ttk.Button(frame, text="Back to Dashboard", command=on_back).pack(pady=5)

    def clear(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def add_stock(self, ticker, shares):
        self.table.insert("", "end", values=(ticker, shares))


# Window GUI stuff
class Dashboard:
    def __init__(self, dframe, signout, on_portfolio_click, on_add_portfolio, on_next_day):
        self.dframe = dframe
        self.label = ttk.Label(self.dframe, text='Dashboard')
        self.label.pack(pady=5)

        self.money = tk.Label(self.dframe, text='Money: $0')
        self.money.pack(pady=5)

        # ---- Portfolio table ----
        self.portfolio_frame = ttk.Frame(self.dframe)
        self.portfolio_frame.pack(fill="both", expand=True, pady=10)

        columns = ("name", "money")
        self.portfolio_table = ttk.Treeview(
            self.portfolio_frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.portfolio_table.heading("name", text="Portfolio")
        self.portfolio_table.heading("money", text="Money ($)")

        self.portfolio_table.column("name", width=200)
        self.portfolio_table.column("money", width=120, anchor="e")

        self.portfolio_table.pack(fill="both", expand=True)

        self.portfolio_table.bind(
            "<Double-1>",
            lambda e: on_portfolio_click(self.get_selected_portfolio())
        )
        
        # ---- Buttons ----
        btn_frame = ttk.Frame(self.dframe)
        btn_frame.pack(pady=5)

        ttk.Button(
            btn_frame,
            text="New Portfolio",
            command=on_add_portfolio
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Next Day",
            command=on_next_day
        ).pack(side="left", padx=5)


        self.signout_button = ttk.Button(self.dframe, text='signout', command=signout)
        self.signout_button.pack(pady=5)

    def clear_portfolios(self):
        for row in self.portfolio_table.get_children():
            self.portfolio_table.delete(row)

    def add_portfolio(self, p_id, name, money):
        self.portfolio_table.insert(
            "",
            "end",
            iid=p_id,           # store p_id here (important!)
            values=(name, money)
        )

    def get_selected_portfolio(self):
        selected = self.portfolio_table.focus()
        return selected  # this is p_id (or None)


    

class myGUI:
    def __init__(self, conn):
        self.conn = conn
        self.root = tk.Tk()
        # Bring app to front on macos
        if platform() == 'Darwin':  # How Mac OS X is identified by Python
            system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        self.style = ttk.Style()
        self.root.geometry('1080x720')
        self.root.title('Application')

        self.l1 = tk.Label(self.root, text="hi", width=25)
        self.l1.pack()

        self.quit_button = ttk.Button(
                self.root,
                text='Quit',
                width=25,
                command=self.root.destroy
        )
        self.quit_button.pack(pady=5)

        # set up current day
        self.current_day = date(2024, 1, 1)

        self.day_frame = ttk.Frame(self.root)
        self.day_label = ttk.Label(self.day_frame, text="")
        self.day_label.pack()

        self.update_day_label()
        
        # --------------- Sign in window --------------
        self.signin_frame = ttk.Frame(self.root)
        self.signin_frame.pack(pady=5)

        self.login_frame = ttk.Frame(self.signin_frame)
        self.login_frame.pack(pady=5)

        self.loginfield = ttk.Entry(self.login_frame, width=30)
        self.loginfield.grid(row=0, column=0, padx=(0,10))

        self.loginConfirm = ttk.Button(
                self.login_frame,
                text='login',
                command=self.login
                )
        self.loginConfirm.grid(row=0, column=1)

        self.register_frame = ttk.Frame(self.signin_frame)
        self.register_frame.pack(pady=5)

        self.registerfield_name = ttk.Entry(self.register_frame, width=22)
        self.registerfield_name.grid(row=0, column=0, padx=(0,10))

        self.registerfield_age = ttk.Entry(self.register_frame, width=5)
        self.registerfield_age.grid(row=0, column=1, padx=(0,10))

        self.registerConfirm = ttk.Button(
                self.register_frame,
                text='register',
                command=self.register
                )
        self.registerConfirm.grid(row=0, column=2)
        # ----------------------------------------------

        self.dashboardframe = ttk.Frame(self.root)
        self.dashboard = Dashboard(
            self.dashboardframe,
            self.signout,
            self.open_portfolio,
            self.show_add_portfolio_dialog,
            self.next_day
        )

        self.portfolio_frame = ttk.Frame(self.root)
        self.portfolio_view = PortfolioView(
            self.portfolio_frame,
            self.show_dashboard
        )


        self.root.bind("<Button-1>", self.clear_focus)

        self.root.mainloop()

    def clear_focus(self, event):
        if event.widget == self.root:
            self.root.focus_set()

    def buttonCallback(self):
        self.l1['text'] = 'hello'

    def login(self):
        user_text = self.loginfield.get()
        try:
            cursor = self.conn.cursor(dictionary=True, prepared=True)
            sql = "SELECT username, name, current_day FROM users WHERE username = %s"
            params = (user_text,)
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is not None and row["name"] is not None:
                self.current_user = row["username"]
                self.current_day = row["current_day"]
                self.l1['text'] = row["name"] + " is logged in."
                self.signin_frame.pack_forget()
                self.day_frame.pack(pady=5)
                self.update_day_label()
                self.dashboardframe.pack(pady=5)
                self.load_portfolios(self.current_user)
                self.load_user_money()
            else:
                self.l1['text'] = "User could not be found"
        except Error as e:
            self.l1['text'] = "User could not be found"
        finally:
            cursor.close()

    def register(self):
        user_name = self.registerfield_name.get()
        user_age = self.registerfield_age.get()
        u = User(
                username = user_name,
                name = user_name,
                age = int(user_age),
                current_day = date(2024, 1, 1)
        )
        if insert(self.conn, "users", u):
            self.current_user = user_name
            self.current_day = u.current_day
            self.l1['text'] = "User " + user_name + " created!"
            self.signin_frame.pack_forget()
            self.day_frame.pack(pady=5)
            self.update_day_label()
            self.dashboardframe.pack(pady=5)
            load_portfolios(self.current_user)
            load_user_money()
        else:
            self.l1['text'] = "User " + user_name + " already exists"

    def signout(self):
        self.l1['text'] = "Signed out."
        self.day_frame.pack_forget()
        self.dashboardframe.pack_forget()
        self.signin_frame.pack(pady=5)

    def load_portfolios(self, username):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT p_id, name, money
                FROM portfolios
                WHERE username = %s
                """,
                (username,)
            )
            rows = cursor.fetchall()

            self.dashboard.clear_portfolios()
            for row in rows:
                self.dashboard.add_portfolio(
                    row["p_id"],
                    row["name"],
                    row["money"]
                )
        finally:
            cursor.close()

    def open_portfolio(self, p_id):
        if not p_id:
            return

        self.current_portfolio = p_id
        self.load_portfolio_stocks(p_id)
        self.show_portfolio()


    def show_add_portfolio_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Portfolio")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Portfolio name:").pack(pady=10)

        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack()

        def create():
            name = name_entry.get().strip()
            if not name:
                return
            self.create_portfolio(name)
            dialog.destroy()

        ttk.Button(dialog, text="Create", command=create).pack(pady=15)

    def create_portfolio(self, name):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO portfolios (username, name, money)
                VALUES (%s, %s, 0)
                """,
                (self.current_user, name)
            )
            self.conn.commit()
            self.load_portfolios(self.current_user)
            self.load_user_money()
        finally:
            cursor.close()

    def show_dashboard(self):
        self.portfolio_frame.pack_forget()
        self.dashboardframe.pack(pady=5)

    def show_portfolio(self):
        self.dashboardframe.pack_forget()
        self.portfolio_frame.pack(pady=5, fill="both", expand=True)

    def load_portfolio_stocks(self, p_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT ticker, shares
                FROM portfolio_shares
                WHERE p_id = %s
                """,
                (p_id,)
            )
            rows = cursor.fetchall()

            self.portfolio_view.clear()
            for row in rows:
                self.portfolio_view.add_stock(
                    row["ticker"],
                    row["shares"]
                )
        finally:
            cursor.close()

    def update_day_label(self):
        self.day_label.config(
            text=f"Current Day: {self.current_day.strftime('%B %d, %Y')}"
        )

    def next_day(self):
        self.current_day += timedelta(days=1)
        self.update_day_label()
        self.save_current_day()

    def save_current_day(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE users
                SET current_day = %s
                WHERE username = %s
                """,
                (self.current_day, self.current_user)
            )
            self.conn.commit()
        finally:
            cursor.close()

    def load_user_money(self):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT money
                FROM user_money
                WHERE username = %s
                """,
                (self.current_user,)
            )
            row = cursor.fetchone()
            total = row["money"]
            self.dashboard.money.config(text=f"Money: ${total}")
        finally:
            cursor.close()


# Configuration struct equivalent
class DbConfig:
    def __init__(self,
                 host="127.0.0.1",
                 port=3306,
                 user="root",
                 password="sinatra1",
                 database="cs3260-project"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

def print_sql_error(e: Error, where: str):
    # Print detailed error info
    print(f"[SQL ERROR @ {where}] {e.msg} | errno: {e.errno} | sqlstate: {e.sqlstate}")


# A simple user-row structure
class User:
    def __init__(self, username: str, name: str, age: int, current_day=None):
        self.username = username
        self.name = name
        self.age = age
        self.current_day = current_day or date(2024, 1, 1)

class Portfolio:
    def __init__(self, p_id: int, username: str, name: str, money: int = 0):
        self.p_id = p_id
        self.username = username
        self.name = name
        self.money = money

class Stock:
    def __init__(self, ticker: str, company_id: int):
        self.ticker = ticker
        self.company_id = company_id

class Price:
    def __init__(self, ticker: str, time: str, dollars: int = 0):
        self.ticker = ticker
        self.time = time
        self.dollars = dollars

class Company:
    def __init__(self, company_id: int, employees: int):
        self.company_id = company_id
        self.employees = employees

class Portfolio_Share:
    def __init__(self, p_id: int, ticker: str, shares: int):
        self.p_id = p_id
        self.ticker = ticker
        self.shares = shares

class Store:
    def __init__(self, store_id: int, name: str):
        self.store_id = store_id
        self.name = name

class Item:
    def __init__(self, item_id: int, name: str):
        self.item_id = item_id
        self.name = name

class Items_in_store:
    def __init__(self, item_id: int, store_id: int, price: int, num_in_stock: int):
        self.item_id = item_id
        self.store_id = store_id
        self.price = price
        self.num_in_stock = num_in_stock

class User_inventory:
    def __init__(self, username: str, item_id: int, amount: int):
        self.username = username
        self.item_id = item_id
        self.amount = amount


def ensure_schema_and_tables(conn, cfg: DbConfig):
    """
    Ensures the database schema and table exist.
    If the database does not exist, create it.
    Then switch to using it and create the `users` table if absent.
    """
    cursor = conn.cursor()
    try:
        # Create database if missing
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg.database}`")
        # Use the database
        conn.database = cfg.database
        # Create the table `users`
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL DEFAULT 0 CHECK (age >= 0),
                money INT NOT NULL DEFAULT 0 CHECK (money >= 0),
                current_day DATE NOT NULL DEFAULT '2024-01-01'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolios (
                p_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                money INT NOT NULL DEFAULT 0 CHECK (money >= 0),

                CONSTRAINT fk_portfolio_user
                    FOREIGN KEY (username) REFERENCES users(username)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                company_id INT PRIMARY KEY,
                employees INT NOT NULL CHECK (employees >= 0)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stocks (
                ticker VARCHAR(10) PRIMARY KEY,
                company_id INT NOT NULL,

                CONSTRAINT fk_stock_company
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prices (
                ticker VARCHAR(10) NOT NULL,
                time DATETIME NOT NULL,
                dollars INT NOT NULL CHECK (dollars >= 0),

                PRIMARY KEY (ticker, time),
                CONSTRAINT fk_price_stock
                    FOREIGN KEY (ticker) REFERENCES stocks(ticker)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_shares (
                p_id INT NOT NULL,
                ticker VARCHAR(10) NOT NULL,
                shares INT NOT NULL CHECK (shares >= 0),

                PRIMARY KEY (p_id, ticker),
                CONSTRAINT fk_ps_portfolio
                    FOREIGN KEY (p_id) REFERENCES portfolios(p_id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_ps_stock
                    FOREIGN KEY (ticker) REFERENCES stocks(ticker)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stores (
                store_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS items_in_store (
                item_id INT NOT NULL,
                store_id INT NOT NULL,
                price INT NOT NULL CHECK (price >= 0),
                num_in_stock INT NOT NULL CHECK (num_in_stock >= 0),

                PRIMARY KEY (item_id, store_id),
                CONSTRAINT fk_iis_item
                    FOREIGN KEY (item_id) REFERENCES items(item_id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_iis_store
                    FOREIGN KEY (store_id) REFERENCES stores(store_id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_inventory (
                username VARCHAR(50) NOT NULL,
                item_id INT NOT NULL,
                amount INT NOT NULL CHECK (amount >= 0),

                PRIMARY KEY (username, item_id),

                CONSTRAINT fk_ui_user
                    FOREIGN KEY (username)
                    REFERENCES users(username)
                    ON DELETE CASCADE,

                CONSTRAINT fk_ui_item
                    FOREIGN KEY (item_id)
                    REFERENCES items(item_id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS user_money AS
            SELECT
                u.username,
                COALESCE(SUM(p.money), 0) AS money
            FROM users u
            LEFT JOIN portfolios p
                ON p.username = u.username
            GROUP BY u.username
            """
        )
        conn.commit()
    except Error as e:
        print_sql_error(e, "ensure_schema_and_tables")
        raise
    finally:
        cursor.close()

def insert(conn, table: str, obj) -> bool:
    firsthalf = "INSERT INTO " + table + " ("
    secondhalf = ") VALUES ("
    values = []
    for name, value in vars(obj).items():
        if (not (name.startswith('__') or callable(value))) and value is not None:
            firsthalf += name + ", "
            secondhalf += "%s, "
            values.append(value)

    sql = firsthalf[:-2] + secondhalf[:-2] + ");"
    params = tuple(values)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()
        return True;
    except Error as e:
        conn.rollback()
        return False;
    finally:
        cursor.close()

def main():
    cfg = DbConfig()
    try:
        # Step 1: Connect to MySQL server (without specifying database yet)
        conn = mysql.connector.connect(
            host=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password
            #database=cfg.database
        )
        if conn.is_connected():
            print("Successfully connected to MySQL server")
        else:
            print("Failed to connect to MySQL server")
            return

        # Step 2: Ensure schema & table exist
        ensure_schema_and_tables(conn, cfg)

        # Step 3: Clear existing rows (for demo only)
        # cursor = conn.cursor()
        # cursor.execute("DELETE FROM users")
        # conn.commit()
        # cursor.close()

        gui = myGUI(conn)
    except Error as e:
        print_sql_error(e, "main")
    except Exception as e:
        print(f"[STD ERROR] {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("MySQL connection closed.")


if __name__ == "__main__":
    main()
