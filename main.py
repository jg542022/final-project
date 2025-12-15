import mysql.connector
from mysql.connector import Error
import tkinter as tk
import tkinter.ttk as ttk
from os import system
from platform import system as platform
from datetime import date, timedelta

class StoreItemsView:
    def __init__(self, frame, on_back_to_shops, on_dashboard, on_inventory, on_buy):
        self.frame = frame
        self.on_buy = on_buy
        
        # Store Name Label (updated dynamically)
        self.title_label = ttk.Label(frame, text="Store")
        self.title_label.pack(pady=5)

        self.money_label = ttk.Label(frame, text="Money: $--")
        self.money_label.pack(pady=5)

        # ---- Items Table ----
        columns = ("name", "price", "stock", "action")
        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=10
        )

        self.table.heading("name", text="Item Name")
        self.table.heading("price", text="Price")
        self.table.heading("stock", text="Stock")
        self.table.heading("action", text="Action")

        self.table.column("name", width=150)
        self.table.column("price", width=80, anchor="e")
        self.table.column("stock", width=60, anchor="center")
        self.table.column("action", width=80, anchor="center")

        self.table.pack(fill="both", expand=True, pady=10)

        self.table.bind("<Button-1>", self.on_click)

        # ---- Buttons ----
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(
            btn_frame,
            text="<- Back to Shops",
            command=on_back_to_shops
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="My Inventory",
            command=on_inventory
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Dashboard",
            command=on_dashboard
        ).pack(side="left", padx=5)

    def clear(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def set_store_name(self, name):
        self.title_label.config(text=f"Welcome to {name}")

    def update_money(self, amount):
        self.money_label.config(text=f"Money: ${amount}")

    def add_item(self, item_id, name, price, stock):
        status = "Buy" if stock > 0 else "Out of Stock"
        
        self.table.insert(
            "", 
            "end", 
            iid=item_id, 
            values=(name, f"${price}", stock, status)
        )

    def on_click(self, event):
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        column = self.table.identify_column(event.x)
        # identify_row returns the 'iid' which we set to item_id
        item_id = self.table.identify_row(event.y)
        
        # Action is column #4
        if column == "#4" and item_id:
            # Prevent clicking if it says "Out of Stock"
            item_values = self.table.item(item_id, "values")
            if item_values[3] == "Buy":
                self.on_buy(item_id)

class ShopView:
    def __init__(self, frame, on_back, on_inventory, on_store_click):
        self.frame = frame
        self.on_store_click = on_store_click

        ttk.Label(frame, text="Select a Store").pack(pady=5)

        # Money Label
        self.money_label = ttk.Label(frame, text="Money: $--")
        self.money_label.pack(pady=5)

        # ---- Stores Table ----
        columns = ("id", "store_name")
        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=10
        )

        self.table.heading("id", text="ID")
        self.table.heading("store_name", text="Store Name")

        self.table.column("id", width=50, anchor="center")
        self.table.column("store_name", width=200)

        self.table.pack(fill="both", expand=True, pady=10)
        
        # Bind click event
        self.table.bind("<Double-1>", self.on_double_click)

        # ---- Buttons ----
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        ttk.Button(
            btn_frame,
            text="My Inventory",
            command=on_inventory
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Back to Dashboard",
            command=on_back
        ).pack(side="left", padx=5)

    def clear(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def add_store(self, store_id, name):
        self.table.insert("", "end", values=(store_id, name))

    def update_money(self, amount):
        self.money_label.config(text=f"Money: ${amount}")

    def on_double_click(self, event):
        selected_item = self.table.focus()
        if selected_item:
            store_data = self.table.item(selected_item, "values")
            # store_data is (store_id, store_name)
            if store_data:
                self.on_store_click(store_data[0], store_data[1])

class PickStocksView:
    def __init__(self, frame, on_back, on_prev, on_next, on_search, on_buy):
        self.frame = frame
        self.on_buy = on_buy
        self.action_buttons = {}

        ttk.Label(frame, text="Pick Stocks").pack(pady=5)

        self.money_label = ttk.Label(frame, text="Money: $--")
        self.money_label.pack(pady=5)
    
        # ---- Search bar ----
        search_frame = ttk.Frame(frame)
        search_frame.pack(pady=5)

        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(
            search_frame,
            text="Search",
            command=lambda: on_search(self.search_entry.get())
        ).pack(side="left")

        # ---- Stocks table ----
        columns = ("ticker", "company", "price", "history", "action")
        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=10
        )

        self.table.heading("ticker", text="Ticker")
        self.table.heading("company", text="Company Name")
        self.table.heading("price", text="Price")
        self.table.heading("history", text="History")
        self.table.heading("action", text="Action")

        self.table.column("ticker", width=80)
        self.table.column("company", width=150)
        self.table.column("price", width=80)
        self.table.column("history", width=100)
        self.table.column("action", width=80)

        self.table.pack(fill="both", expand=True, pady=10)

        self.table.bind("<Button-1>", self.on_click)

        # ---- Paging + back ----
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(pady=5)

        self.prev_btn = ttk.Button(nav_frame, text="<- Prev", command=on_prev)
        self.prev_btn.pack(side="left", padx=5)
        self.next_btn = ttk.Button(nav_frame, text="Next ->", command=on_next)
        self.next_btn.pack(side="left", padx=5)

        ttk.Button(
            frame,
            text="Back to Portfolio",
            command=on_back
        ).pack(pady=5)

    def clear(self):
        for btn in self.action_buttons.values():
            btn.destroy()
        self.action_buttons.clear()

        for row in self.table.get_children():
            self.table.delete(row)

    def add_stock(self, ticker, company_name, price):
        display_price = f"${price}" if price is not None else "—"
        self.table.insert(
        "",
        "end",
        values=(ticker, company_name, display_price, "", "Buy")
    )

    def on_click(self, event):
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)

        # Action column is column #5
        if column == "#5" and row:
            item = self.table.item(row, "values")
            ticker = item[0]
            price_str = item[2]

            # Parse price (remove '$' and convert to int)
            if price_str == "—":
                print("Cannot buy stock with no price")
                return
            
            try:
                # Remove '$' and commas if present
                price = int(float(price_str.replace('$', '').replace(',', '')))
                self.on_buy(ticker, price) # Trigger the callback
            except ValueError:
                print("Error parsing price")

    def update_nav_buttons(self, page, last_page):
        self.prev_btn.config(state="normal" if page > 0 else "disabled")
        self.next_btn.config(state="normal" if page < last_page else "disabled")

    def update_money(self, amount):
        self.money_label.config(text=f"Money: ${amount}")

class InventoryView:
    def __init__(self, frame, on_back, on_shop):
        self.frame = frame

        ttk.Label(frame, text="My Inventory").pack(pady=5)

        # ---- Inventory Table ----
        columns = ("item", "quantity")
        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=10
        )

        self.table.heading("item", text="Item Name")
        self.table.heading("quantity", text="Quantity")

        self.table.column("item", width=200)
        self.table.column("quantity", width=100, anchor="center")

        self.table.pack(fill="both", expand=True, pady=10)

        # ---- Buttons ----
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        ttk.Button(
            btn_frame,
            text="Go to Shop",
            command=on_shop
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Back to Dashboard",
            command=on_back
        ).pack(pady=5)

    def clear(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def add_item(self, name, quantity):
        self.table.insert("", "end", values=(name, quantity))

class PortfolioView:
    def __init__(self, frame, on_back, on_pick_stocks, on_sell):
        self.frame = frame
        self.on_sell = on_sell

        ttk.Label(frame, text="Portfolio").pack(pady=5)

        self.money_label = ttk.Label(frame, text="Money: $--")
        self.money_label.pack(pady=5)

        # ---- Stock table ----
        columns = ("ticker", "company", "shares", "value", "action")
        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.table.heading("ticker", text="Ticker")
        self.table.heading("company", text="Company Name")
        self.table.heading("shares", text="Shares")
        self.table.heading("value", text="Value")
        self.table.heading("action", text="Action")

        self.table.column("ticker", width=80)
        self.table.column("company", width=150)
        self.table.column("shares", width=80, anchor="e")
        self.table.column("value", width=100, anchor="e")
        self.table.column("action", width=100, anchor="center")
        self.table.pack(fill="both", expand=True, pady=10)

        self.table.bind("<Button-1>", self.on_click)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        ttk.Button(
                btn_frame,
                text="Pick Stocks",
                command=on_pick_stocks
        ).pack(side="left", padx=5)

        ttk.Button(
                frame,
                text="Back to Dashboard",
                command=on_back
        ).pack(side="left", padx=5)

    def clear(self):
        for row in self.table.get_children():
            self.table.delete(row)

    def add_stock(self, ticker, company_name, shares, price):
        if price is not None:
            total_value = shares * price
            display_value = f"${total_value}"
        else:
            display_value = "—"
            
        self.table.insert(
            "", 
            "end", 
            values=(ticker, company_name, shares, display_value, "Sell")
        )

    def on_click(self, event):
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.table.identify_column(event.x)
        row = self.table.identify_row(event.y)

        # "Action" is column #5
        if column == "#5" and row:
            item = self.table.item(row, "values")
            ticker = item[0]
            # Call the sell callback
            self.on_sell(ticker)

    def update_money(self, amount):
        self.money_label.config(text=f"Money: ${amount}")


# Window GUI stuff
class Dashboard:
    def __init__(self, dframe, signout, on_portfolio_click, on_add_portfolio, on_next_day, on_inventory, on_shop):
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

        ttk.Button(
            btn_frame,
            text="Shop",
            command=on_shop
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Inventory",
            command=on_inventory
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
            self.next_day,
            self.show_inventory,
            self.show_shop
        )

        self.portfolio_frame = ttk.Frame(self.root)
        self.portfolio_view = PortfolioView(
            self.portfolio_frame,
            self.show_dashboard,
            self.show_pick_stocks,
            self.sell_stock
        )

        self.shop_frame = ttk.Frame(self.root)
        self.shop_view = ShopView(
            self.shop_frame,
            self.show_dashboard,
            self.show_inventory,
            self.open_store
        )

        self.inventory_frame = ttk.Frame(self.root)
        self.inventory_view = InventoryView(
            self.inventory_frame,
            self.show_dashboard,
            self.show_shop
        )

        self.store_items_frame = ttk.Frame(self.root)
        self.store_items_view = StoreItemsView(
            self.store_items_frame,
            self.show_shop,       
            self.show_dashboard,
            self.show_inventory,
            self.buy_item
        )

        self.stock_page = 0
        self.stocks_per_page = 15
        self.total_stocks = 0
        self.last_stock_page = 0
        self.stock_search_query = None

        self.pick_stocks_frame = ttk.Frame(self.root)
        self.pick_stocks_view = PickStocksView(
            self.pick_stocks_frame,
            self.show_portfolio,
            self.prev_stock_page,
            self.next_stock_page,
            self.search_stocks,
            self.buy_stock
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
        self.store_items_frame.pack_forget()
        self.inventory_frame.pack_forget()
        self.pick_stocks_frame.pack_forget()
        self.shop_frame.pack_forget()
        self.load_portfolios(self.current_user)
        self.dashboardframe.pack(pady=5)

    def load_portfolio_stocks(self, p_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT 
                    ps.ticker, 
                    ps.shares,
                    c.name as company_name,
                    (
                        SELECT p.dollars 
                        FROM prices p 
                        WHERE p.ticker = ps.ticker 
                          AND p.time < DATE_ADD(%s, INTERVAL 1 DAY)
                        ORDER BY p.time DESC 
                        LIMIT 1
                    ) as price
                FROM portfolio_shares ps
                JOIN stocks s ON ps.ticker = s.ticker
                JOIN companies c ON s.company_id = c.company_id
                WHERE ps.p_id = %s
                """,
                (self.current_day, p_id)
            )
            rows = cursor.fetchall()

            self.portfolio_view.clear()
            for row in rows:
                self.portfolio_view.add_stock(
                    row["ticker"],
                    row["company_name"], # Pass the new name
                    row["shares"],
                    row["price"]
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
        self.load_portfolios(self.current_user)

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
                FROM users
                WHERE username = %s
                """,
                (self.current_user,)
            )
            row = cursor.fetchone()
            self.usermoney = row["money"]
            self.dashboard.money.config(text=f"Money: ${self.usermoney}")
        finally:
            cursor.close()

    def show_pick_stocks(self):
        self.portfolio_frame.pack_forget()

        self.stock_page = 0
        self.update_stock_count()
        self.load_stocks_page()

        self.pick_stocks_view.update_money(self.usermoney)

        self.pick_stocks_frame.pack(pady=5, fill="both", expand=True)

    def show_portfolio(self):
        self.pick_stocks_frame.pack_forget()
        self.dashboardframe.pack_forget()

        if hasattr(self, 'current_portfolio') and self.current_portfolio:
            self.load_portfolio_stocks(self.current_portfolio)

        self.portfolio_view.update_money(self.usermoney)
        self.load_portfolios(self.current_user)

        self.portfolio_frame.pack(pady=5, fill="both", expand=True)

    def load_stocks_page(self):
        offset = self.stock_page * self.stocks_per_page
        cursor = self.conn.cursor(dictionary=True)
        try:
            # Base query parts
            # We select c.name as company_name
            # We JOIN companies c ON s.company_id = c.company_id
            sql = """
                SELECT 
                    s.ticker, 
                    c.name as company_name,
                    (
                        SELECT p.dollars 
                        FROM prices p 
                        WHERE p.ticker = s.ticker 
                          AND p.time < DATE_ADD(%s, INTERVAL 1 DAY)
                        ORDER BY p.time DESC 
                        LIMIT 1
                    ) AS price
                FROM stocks s
                JOIN companies c ON s.company_id = c.company_id
                WHERE s.ticker LIKE %s
                ORDER BY s.ticker
                LIMIT %s OFFSET %s
            """
            
            # (Logic for search query vs empty query remains, just update SQL)
            search = (self.stock_search_query if self.stock_search_query else "") + "%"
            
            cursor.execute(sql, (self.current_day, search, self.stocks_per_page, offset))
            rows = cursor.fetchall()

            self.pick_stocks_view.clear()
            for row in rows:
                self.pick_stocks_view.add_stock(
                    row["ticker"],
                    row["company_name"],  # Pass the new name
                    row["price"]
                )
        finally:
            cursor.close()

    def next_stock_page(self):
        self.stock_page += 1
        self.load_stocks_page()

    def prev_stock_page(self):
        if self.stock_page > 0:
            self.stock_page -= 1
            self.load_stocks_page()

    def update_stock_count(self):
        cursor = self.conn.cursor()
        try:
            if self.stock_search_query:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM stocks
                    WHERE ticker LIKE %s
                    """,
                    (self.stock_search_query + "%",)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM stocks")

            (count,) = cursor.fetchone()
            self.total_stocks = count
            self.last_stock_page = max(
                0,
                (self.total_stocks - 1) // self.stocks_per_page
            )
        finally:
            cursor.close()


    def search_stocks(self, query):
        query = query.strip().upper()

        # Empty search = reset
        if not query:
            self.stock_search_query = None
        else:
            self.stock_search_query = query

        self.stock_page = 0
        self.update_stock_count()
        self.load_stocks_page()

    def update_user_money(conn, username, delta):
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE users
                SET money = money + %s
                WHERE username = %s
                """,
                (delta, username)
            )
            conn.commit()
        finally:
            cursor.close()

    def get_user_money(conn, username):
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT money FROM users WHERE username = %s",
                (username,)
            )
            return cursor.fetchone()["money"]
        finally:
            cursor.close()

    def buy_stock(self, ticker, price):
        # Validation checks
        if not hasattr(self, 'current_portfolio') or not self.current_portfolio:
            print("No portfolio selected.") 
            self.l1['text'] = "Error: No portfolio selected."
            return

        if self.usermoney < price:
            print(f"Insufficient funds. Need ${price}, have ${self.usermoney}")
            self.l1['text'] = "Insufficient funds!"
            return

        cursor = self.conn.cursor()
        try:
            # 1. Deduct money from users table
            cursor.execute(
                "UPDATE users SET money = money - %s WHERE username = %s",
                (price, self.current_user)
            )

            # 2. Add stock to portfolio_shares
            # We use ON DUPLICATE KEY UPDATE to increment shares if the row exists
            cursor.execute(
                """
                INSERT INTO portfolio_shares (p_id, ticker, shares)
                VALUES (%s, %s, 1)
                ON DUPLICATE KEY UPDATE shares = shares + 1
                """,
                (self.current_portfolio, ticker)
            )

            self.conn.commit()

            # 3. Update local GUI state
            self.usermoney -= price

            self.dashboard.money.config(text=f"Money: ${self.usermoney}")

            self.pick_stocks_view.update_money(self.usermoney)

            self.l1['text'] = f"Bought 1 share of {ticker}!"
            print(f"Successfully bought {ticker} for ${price}")

        except Error as e:
            self.conn.rollback()
            print(f"Transaction failed: {e}")
            self.l1['text'] = "Transaction failed."
        finally:
            cursor.close()

    def sell_stock(self, ticker):
        if not hasattr(self, 'current_portfolio') or not self.current_portfolio:
            return

        cursor = self.conn.cursor(dictionary=True)
        try:
            # 1. Get current price and shares owned
            cursor.execute(
                """
                SELECT 
                    ps.shares,
                    (
                        SELECT p.dollars FROM prices p 
                        WHERE p.ticker = ps.ticker AND DATE(p.time) <= %s 
                        ORDER BY p.time DESC LIMIT 1
                    ) as price
                FROM portfolio_shares ps
                WHERE ps.p_id = %s AND ps.ticker = %s
                """,
                (self.current_day, self.current_portfolio, ticker)
            )
            row = cursor.fetchone()
            
            if not row or row['shares'] < 1:
                print("Error: You don't own this stock.")
                return
            
            price = row['price']
            if price is None:
                print("Error: Cannot sell stock with no price data.")
                return

            # 2. Perform Transaction
            # Update User Money
            cursor.execute(
                "UPDATE users SET money = money + %s WHERE username = %s",
                (price, self.current_user)
            )

            # Update Shares (Delete row if 0 shares remaining)
            if row['shares'] == 1:
                cursor.execute(
                    "DELETE FROM portfolio_shares WHERE p_id = %s AND ticker = %s",
                    (self.current_portfolio, ticker)
                )
            else:
                cursor.execute(
                    "UPDATE portfolio_shares SET shares = shares - 1 WHERE p_id = %s AND ticker = %s",
                    (self.current_portfolio, ticker)
                )

            self.conn.commit()

            # 3. Update UI
            self.usermoney += price
            self.portfolio_view.update_money(self.usermoney)
            self.dashboard.money.config(text=f"Money: ${self.usermoney}")
            self.l1['text'] = f"Sold 1 share of {ticker} for ${price}!"
            
            # Refresh table
            self.load_portfolio_stocks(self.current_portfolio)

        except Error as e:
            self.conn.rollback()
            print(f"Sell failed: {e}")
            self.l1['text'] = "Sell transaction failed."
        finally:
            cursor.close()

    def show_inventory(self):
        self.dashboardframe.pack_forget()
        self.portfolio_frame.pack_forget()
        self.store_items_frame.pack_forget()
        self.pick_stocks_frame.pack_forget()
        self.shop_frame.pack_forget()
        
        self.load_inventory()

        self.inventory_frame.pack(pady=5, fill="both", expand=True)

    def load_inventory(self):
        cursor = self.conn.cursor(dictionary=True)
        try:
            # Join user_inventory with items to get the name
            cursor.execute(
                """
                SELECT i.name, ui.amount
                FROM user_inventory ui
                JOIN items i ON ui.item_id = i.item_id
                WHERE ui.username = %s
                  AND ui.amount > 0
                ORDER BY i.name
                """,
                (self.current_user,)
            )
            rows = cursor.fetchall()

            self.inventory_view.clear()
            for row in rows:
                self.inventory_view.add_item(
                    row["name"],
                    row["amount"]
                )
        except Error as e:
            print(f"Failed to load inventory: {e}")
        finally:
            cursor.close()

    def load_stores(self):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT store_id, name FROM stores ORDER BY name")
            rows = cursor.fetchall()
            
            self.shop_view.clear()
            for row in rows:
                self.shop_view.add_store(row["store_id"], row["name"])
                
            # Update money display
            self.shop_view.update_money(self.usermoney)
        finally:
            cursor.close()

    def show_shop(self):
        # Hide all other frames
        self.dashboardframe.pack_forget()
        self.portfolio_frame.pack_forget()
        self.store_items_frame.pack_forget()
        self.pick_stocks_frame.pack_forget()
        self.inventory_frame.pack_forget()

        self.load_stores()
        self.shop_frame.pack(pady=5, fill="both", expand=True)

    def open_store(self, store_id, store_name):
        self.shop_frame.pack_forget()
        
        self.store_items_view.set_store_name(store_name)
        self.load_store_items(store_id)
        
        self.store_items_frame.pack(pady=5, fill="both", expand=True)
        
        self.current_store_id = store_id

    def load_store_items(self, store_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT i.item_id, i.name, iis.price, iis.num_in_stock
                FROM items_in_store iis
                JOIN items i ON iis.item_id = i.item_id
                WHERE iis.store_id = %s
                ORDER BY i.name
                """,
                (store_id,)
            )
            rows = cursor.fetchall()

            self.store_items_view.clear()
            for row in rows:
                self.store_items_view.add_item(
                    row["item_id"],
                    row["name"],
                    row["price"],
                    row["num_in_stock"]
                )
            self.store_items_view.update_money(self.usermoney)
        finally:
            cursor.close()

    def buy_item(self, item_id):
        if not hasattr(self, 'current_store_id'):
            return

        cursor = self.conn.cursor(dictionary=True)
        try:
            # 1. Check Price and Stock from DB (to prevent stale data issues)
            cursor.execute(
                """
                SELECT price, num_in_stock 
                FROM items_in_store 
                WHERE item_id = %s AND store_id = %s
                """,
                (item_id, self.current_store_id)
            )
            item = cursor.fetchone()
            
            if not item:
                print("Item not found.")
                return

            price = item['price']
            stock = item['num_in_stock']

            # 2. Validation
            if stock <= 0:
                print("Item is out of stock.")
                self.l1['text'] = "Item is out of stock!"
                return
            
            if self.usermoney < price:
                print("Insufficient funds.")
                self.l1['text'] = "Insufficient funds!"
                return

            # 3. Perform Transaction
            
            # Deduct Money
            cursor.execute(
                "UPDATE users SET money = money - %s WHERE username = %s",
                (price, self.current_user)
            )

            # Decrease Stock
            cursor.execute(
                """
                UPDATE items_in_store 
                SET num_in_stock = num_in_stock - 1 
                WHERE item_id = %s AND store_id = %s
                """,
                (item_id, self.current_store_id)
            )

            # Add to User Inventory (Upsert)
            cursor.execute(
                """
                INSERT INTO user_inventory (username, item_id, amount)
                VALUES (%s, %s, 1)
                ON DUPLICATE KEY UPDATE amount = amount + 1
                """,
                (self.current_user, item_id)
            )

            self.conn.commit()

            # 4. Update UI
            self.usermoney -= price
            
            # Update Dashboard/Global labels
            self.dashboard.money.config(text=f"Money: ${self.usermoney}")
            self.store_items_view.update_money(self.usermoney)
            self.l1['text'] = "Purchase successful!"
            
            # Refresh the table (updates stock count)
            self.load_store_items(self.current_store_id)

        except Error as e:
            self.conn.rollback()
            print(f"Purchase failed: {e}")
            self.l1['text'] = "Purchase failed."
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
    def __init__(self, company_id: int, name: str):
        self.company_id = company_id
        self.name = name

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
                name VARCHAR(100) NOT NULL DEFAULT 'Unknown'
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
        cursor.execute("DROP FUNCTION IF EXISTS calc_portfolio_value")
        cursor.execute(
            """
            CREATE FUNCTION calc_portfolio_value(param_p_id INT, param_date DATE) 
            RETURNS INT
            DETERMINISTIC
            READS SQL DATA
            BEGIN
                DECLARE total_val INT;
                
                SELECT COALESCE(SUM(
                    ps.shares * (
                        SELECT pr.dollars 
                        FROM prices pr 
                        WHERE pr.ticker = ps.ticker 
                          AND pr.time < DATE_ADD(param_date, INTERVAL 1 DAY)
                        ORDER BY pr.time DESC 
                        LIMIT 1
                    )
                ), 0) INTO total_val
                FROM portfolio_shares ps
                WHERE ps.p_id = param_p_id;
                
                RETURN total_val;
            END
            """
        )
        cursor.execute("DROP TRIGGER IF EXISTS trg_user_next_day")
        cursor.execute(
            """
            CREATE TRIGGER trg_user_next_day
            AFTER UPDATE ON users
            FOR EACH ROW
            BEGIN
                IF OLD.current_day <> NEW.current_day THEN
                    UPDATE portfolios 
                    SET money = calc_portfolio_value(p_id, NEW.current_day)
                    WHERE username = NEW.username;
                END IF;
            END
            """
        )
        cursor.execute("DROP TRIGGER IF EXISTS trg_shares_insert")
        cursor.execute(
            """
            CREATE TRIGGER trg_shares_insert
            AFTER INSERT ON portfolio_shares
            FOR EACH ROW
            BEGIN
                -- Get the user's date
                DECLARE user_date DATE;
                SELECT current_day INTO user_date FROM users 
                WHERE username = (SELECT username FROM portfolios WHERE p_id = NEW.p_id);
                
                UPDATE portfolios 
                SET money = calc_portfolio_value(NEW.p_id, user_date)
                WHERE p_id = NEW.p_id;
            END
            """
        )
        cursor.execute("DROP TRIGGER IF EXISTS trg_shares_update")
        cursor.execute(
            """
            CREATE TRIGGER trg_shares_update
            AFTER UPDATE ON portfolio_shares
            FOR EACH ROW
            BEGIN
                DECLARE user_date DATE;
                SELECT current_day INTO user_date FROM users 
                WHERE username = (SELECT username FROM portfolios WHERE p_id = NEW.p_id);
                
                UPDATE portfolios 
                SET money = calc_portfolio_value(NEW.p_id, user_date)
                WHERE p_id = NEW.p_id;
            END
            """
        )
        cursor.execute("DROP TRIGGER IF EXISTS trg_shares_delete")
        cursor.execute(
            """
            CREATE TRIGGER trg_shares_delete
            AFTER DELETE ON portfolio_shares
            FOR EACH ROW
            BEGIN
                DECLARE user_date DATE;
                SELECT current_day INTO user_date FROM users 
                WHERE username = (SELECT username FROM portfolios WHERE p_id = OLD.p_id);
                
                UPDATE portfolios 
                SET money = calc_portfolio_value(OLD.p_id, user_date)
                WHERE p_id = OLD.p_id;
            END
            """
        )
        conn.commit()
        create_index_if_missing(conn, "idx_stocks_ticker", "stocks", "ticker")
        create_index_if_missing(conn, "idx_prices_ticker_time", "prices", "ticker, time")
    except Error as e:
        print_sql_error(e, "ensure_schema_and_tables")
        raise
    finally:
        cursor.close()

def create_index_if_missing(conn, index_name, table, columns):
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT(1)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE table_schema = DATABASE()
              AND table_name = %s
              AND index_name = %s
            """,
            (table, index_name)
        )
        exists = cursor.fetchone()[0]

        if not exists:
            cursor.execute(
                f"CREATE INDEX {index_name} ON {table}({columns})"
            )
            conn.commit()
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
