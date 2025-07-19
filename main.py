import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox, ttk
import sys

#Database Configuration 
DB_CONFIG = {
    'host': 'localhost',
    'database': 'ecommerce_db',
    'user': 'root',    
    'password': 'Akshat9091' 
}


def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("Database Connection Error", f"Could not connect to MySQL database:\n{e}\nPlease check your database server and credentials.")
        return None

def close_db_connection(conn):
    """Close the database connection."""
    if conn and conn.is_connected():
        conn.close()


class Category:
    def __init__(self, category_id, name):
        self.category_id = category_id
        self.name = name


class Product:
    def __init__(self, product_id, name, description, price, stock_quantity, category_id, category_name=None):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
        self.category_id = category_id
        self.category_name = category_name 


class InventoryManager:
    def __init__(self):
        self.conn = get_db_connection()
        if not self.conn:
            raise ConnectionError("Failed to establish database connection.")

    def __del__(self):
        self.close()

    def close(self):
        close_db_connection(self.conn)

   
    def add_category(self, name):
        try:
            cursor = self.conn.cursor()
            query = "INSERT INTO categories (name) VALUES (%s)"
            cursor.execute(query, (name,))
            self.conn.commit()
            return cursor.lastrowid 
        except Error as e:
            if e.errno == 1062: 
                raise ValueError(f"Category '{name}' already exists.")
            else:
                raise Error(f"Error adding category: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def get_all_categories(self):
        categories = []
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT category_id, name FROM categories ORDER BY name"
            cursor.execute(query)
            for row in cursor:
                categories.append(Category(row['category_id'], row['name']))
        except Error as e:
            raise Error(f"Error retrieving categories: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
        return categories

    def get_category_by_id(self, category_id):
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT category_id, name FROM categories WHERE category_id = %s"
            cursor.execute(query, (category_id,))
            row = cursor.fetchone()
            if row:
                return Category(row['category_id'], row['name'])
            return None
        except Error as e:
            raise Error(f"Error retrieving category: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def update_category(self, category_id, new_name):
        try:
            cursor = self.conn.cursor()
            query = "UPDATE categories SET name = %s WHERE category_id = %s"
            cursor.execute(query, (new_name, category_id))
            self.conn.commit()
            return cursor.rowcount > 0 
        except Error as e:
            if e.errno == 1062: 
                raise ValueError(f"Category name '{new_name}' already exists.")
            else:
                raise Error(f"Error updating category: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def delete_category(self, category_id):
        try:
            cursor = self.conn.cursor()
            
            check_query = "SELECT COUNT(*) FROM products WHERE category_id = %s"
            cursor.execute(check_query, (category_id,))
            product_count = cursor.fetchone()[0]

            if product_count > 0:
                raise ValueError(f"Cannot delete category ID {category_id}: It has {product_count} product(s) associated.")

            query = "DELETE FROM categories WHERE category_id = %s"
            cursor.execute(query, (category_id,))
            self.conn.commit()
            return cursor.rowcount > 0 
        except Error as e:
            raise Error(f"Error deleting category: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    
    def add_product(self, name, description, price, stock_quantity, category_id):
        try:
            cursor = self.conn.cursor()
            query = ("INSERT INTO products (name, description, price, stock_quantity, category_id) "
                     "VALUES (%s, %s, %s, %s, %s)")
            cursor.execute(query, (name, description, price, stock_quantity, category_id))
            self.conn.commit()
            return cursor.lastrowid
        except Error as e:
            if e.errno == 1062: 
                raise ValueError(f"Product '{name}' already exists.")
            elif e.errno == 1452: 
                raise ValueError(f"Category ID {category_id} does not exist. Please add the category first.")
            else:
                raise Error(f"Error adding product: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def get_all_products(self):
        products = []
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT p.product_id, p.name, p.description, p.price, p.stock_quantity, p.category_id, c.name AS category_name
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
                ORDER BY p.name
            """
            cursor.execute(query)
            for row in cursor:
                products.append(Product(
                    row['product_id'], row['name'], row['description'],
                    row['price'], row['stock_quantity'], row['category_id'],
                    row['category_name']
                ))
        except Error as e:
            raise Error(f"Error retrieving products: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
        return products

    def update_product_stock(self, product_id, new_quantity):
        try:
            cursor = self.conn.cursor()
            query = "UPDATE products SET stock_quantity = %s WHERE product_id = %s"
            cursor.execute(query, (new_quantity, product_id))
            self.conn.commit()
            return cursor.rowcount > 0 
        except Error as e:
            raise Error(f"Error updating product stock: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def delete_product(self, product_id):
        try:
            cursor = self.conn.cursor()
            query = "DELETE FROM products WHERE product_id = %s"
            cursor.execute(query, (product_id,))
            self.conn.commit()
            return cursor.rowcount > 0 
        except Error as e:
            raise Error(f"Error deleting product: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()



class AddCategoryDialog(tk.Toplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.title("Add New Category")
        self.manager = manager
        self.result = None 

        self.create_widgets()

    def create_widgets(self):
        self.geometry("350x150") 
        self.resizable(False, False) 

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Category Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.focus_set() 

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Category", command=self.add_category_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.grab_set()
        self.transient(parent) 
        self.wait_window(self) 

    def add_category_action(self):
        name = self.name_entry.get().strip()

        if not name:
            messagebox.showerror("Input Error", "Category name cannot be empty.", parent=self)
            return

        try:
            self.manager.add_category(name)
            messagebox.showinfo("Success", f"Category '{name}' added successfully!", parent=self)
            self.result = True 
            self.destroy()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve), parent=self)
        except Error as e: 
            messagebox.showerror("Database Error", str(e), parent=self)


class UpdateCategoryDialog(tk.Toplevel):
    def __init__(self, parent, manager, category_id, current_name):
        super().__init__(parent)
        self.title("Update Category")
        self.manager = manager
        self.category_id = category_id
        self.result = None 

        self.create_widgets(current_name)

    def create_widgets(self, current_name):
        self.geometry("350x150") 
        self.resizable(False, False) 

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="New Category Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.insert(0, current_name) 
        self.name_entry.focus_set() 

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Update Category", command=self.update_category_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.grab_set() 
        self.transient(parent) 
        self.wait_window(self) 

    def update_category_action(self):
        new_name = self.name_entry.get().strip()

        if not new_name:
            messagebox.showerror("Input Error", "Category name cannot be empty.", parent=self)
            return

        try:
            if self.manager.update_category(self.category_id, new_name):
                messagebox.showinfo("Success", f"Category ID {self.category_id} updated to '{new_name}'.", parent=self)
                self.result = True 
                self.destroy()
            else:
                messagebox.showwarning("Not Found", f"Category ID {self.category_id} not found.", parent=self)
                self.result = False
        except ValueError as ve: 
            messagebox.showerror("Input Error", str(ve), parent=self)
        except Error as e: 
            messagebox.showerror("Database Error", str(e), parent=self)


class AddProductDialog(tk.Toplevel):
    def __init__(self, parent, manager, categories):
        super().__init__(parent)
        self.title("Add New Product")
        self.manager = manager
        self.categories = categories
        self.result = None 

        self.create_widgets()

    def create_widgets(self):
        self.geometry("450x300") 
        self.resizable(False, False) 

        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

       
        tk.Label(main_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

      
        tk.Label(main_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(main_frame, width=40)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

      
        tk.Label(main_frame, text="Price:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.price_entry = ttk.Entry(main_frame, width=40)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        
        tk.Label(main_frame, text="Stock Quantity:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.stock_entry = ttk.Entry(main_frame, width=40)
        self.stock_entry.grid(row=3, column=1, padx=5, pady=5)

       
        tk.Label(main_frame, text="Category:").grid(row=4, column=0, padx=5, pady=5, sticky="w")

        
        category_names = [cat.name for cat in self.categories]
        self.selected_category_name = tk.StringVar(self)
        if category_names:
            self.selected_category_name.set(category_names[0]) # Default to first category
        else:
            self.selected_category_name.set("No Categories Available")
            messagebox.showwarning("Warning", "No categories found. Please add categories before adding products.", parent=self)
            
            self.name_entry.config(state='disabled')
            self.desc_entry.config(state='disabled')
            self.price_entry.config(state='disabled')
            self.stock_entry.config(state='disabled')


        self.category_dropdown = ttk.Combobox(main_frame, textvariable=self.selected_category_name,
                                               values=category_names, state="readonly", width=37)
        self.category_dropdown.grid(row=4, column=1, padx=5, pady=5)
       

       
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Product", command=self.add_product_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.grab_set() 
        self.transient(parent) 
        self.wait_window(self) 

    def add_product_action(self):
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        price_str = self.price_entry.get().strip()
        stock_str = self.stock_entry.get().strip()
        selected_category_name = self.selected_category_name.get()

        if not all([name, description, price_str, stock_str]) or selected_category_name == "No Categories Available":
            messagebox.showerror("Input Error", "All fields are required and a category must be selected.", parent=self)
            return

        try:
            price = float(price_str)
            stock = int(stock_str)
            if price <= 0:
                messagebox.showerror("Input Error", "Price must be positive.", parent=self)
                return
            if stock < 0:
                messagebox.showerror("Input Error", "Stock quantity cannot be negative.", parent=self)
                return
        except ValueError:
            messagebox.showerror("Input Error", "Price must be a number, Stock must be an integer.", parent=self)
            return

        
        category_id = None
        for cat in self.categories:
            if cat.name == selected_category_name:
                category_id = cat.category_id
                break

        if category_id is None:
            messagebox.showerror("Error", "Selected category not found (this shouldn't happen).", parent=self)
            return

        try:
            self.manager.add_product(name, description, price, stock, category_id)
            messagebox.showinfo("Success", f"Product '{name}' added successfully!", parent=self)
            self.result = True 
            self.destroy()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve), parent=self)
        except Error as e:
            messagebox.showerror("Database Error", str(e), parent=self)


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("E-commerce Product Manager")
        self.geometry("900x600") 
        self.iconbitmap() 

        
        self.style = ttk.Style(self)
        self.style.theme_use('clam') 

       
        BG_LIGHT_GRAY = "#0631F1"
        TEXT_DARK_GRAY = '#333333'
        ACCENT_YELLOW = "#BBFF00"
        ACCENT_BLUE_DARK = "#c0ea01"
        HEADER_GRAY = "#05F7F3"
        BORDER_GRAY = "#000000"

        self.config(bg=BG_LIGHT_GRAY) 

        self.style.configure('TFrame', background=BG_LIGHT_GRAY)
        self.style.configure('TLabelFrame', background=BG_LIGHT_GRAY, foreground=TEXT_DARK_GRAY, font=('Arial', 11, 'bold'))
        self.style.configure('TLabel', background=BG_LIGHT_GRAY, foreground=TEXT_DARK_GRAY)
        self.style.configure('TEntry', fieldbackground='white', foreground=TEXT_DARK_GRAY)
        self.style.configure('TCombobox', fieldbackground='white', foreground=TEXT_DARK_GRAY)

        
        self.style.configure('TButton',
                             font=('Arial', 10),
                             background=ACCENT_YELLOW,
                             foreground='white',
                             padding=5,
                             relief="flat") 
        self.style.map('TButton',
                       background=[('active', ACCENT_BLUE_DARK)],
                       foreground=[('active', 'white')])

        
        self.style.configure('Treeview',
                             background='white',
                             foreground=TEXT_DARK_GRAY,
                             rowheight=25,
                             fieldbackground='white',
                             font=('Arial', 9))
        self.style.configure('Treeview.Heading',
                             font=('Arial', 10, 'bold'),
                             background=HEADER_GRAY,
                             foreground=TEXT_DARK_GRAY,
                             relief="raised")
        self.style.map('Treeview',
                       background=[('selected', ACCENT_YELLOW)],
                       foreground=[('selected', 'white')])

       
        try:
            self.manager = InventoryManager()
        except ConnectionError:
            sys.exit(1) 

        
        self.create_widgets()
        self.load_categories()
        self.load_products()

    def create_widgets(self):
        
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        
        category_frame = ttk.LabelFrame(main_frame, text="Categories")
        category_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.category_tree = ttk.Treeview(category_frame, columns=("ID", "Name"), show="headings")
        self.category_tree.heading("ID", text="ID", anchor=tk.W)
        self.category_tree.heading("Name", text="Name", anchor=tk.W)
        self.category_tree.column("ID", width=50, stretch=tk.NO)
        self.category_tree.column("Name", width=150, stretch=tk.YES)
        self.category_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        cat_btn_frame = ttk.Frame(category_frame)
        cat_btn_frame.pack(pady=5)
        ttk.Button(cat_btn_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(cat_btn_frame, text="Update Category", command=self.update_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(cat_btn_frame, text="Delete Category", command=self.delete_category).pack(side=tk.LEFT, padx=2)

       
        product_frame = ttk.LabelFrame(main_frame, text="Products")
        product_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.product_tree = ttk.Treeview(product_frame, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings")
        self.product_tree.heading("ID", text="ID", anchor=tk.W)
        self.product_tree.heading("Name", text="Name", anchor=tk.W)
        self.product_tree.heading("Category", text="Category", anchor=tk.W)
        self.product_tree.heading("Price", text="Price", anchor=tk.W)
        self.product_tree.heading("Stock", text="Stock", anchor=tk.W)

        self.product_tree.column("ID", width=50, stretch=tk.NO)
        self.product_tree.column("Name", width=150, stretch=tk.YES)
        self.product_tree.column("Category", width=100, stretch=tk.YES)
        self.product_tree.column("Price", width=80, stretch=tk.NO)
        self.product_tree.column("Stock", width=60, stretch=tk.NO)

        self.product_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        prod_btn_frame = ttk.Frame(product_frame)
        prod_btn_frame.pack(pady=5)
        ttk.Button(prod_btn_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(prod_btn_frame, text="Update Stock", command=self.update_product_stock).pack(side=tk.LEFT, padx=2)
        ttk.Button(prod_btn_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=2)

        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3) 
        main_frame.grid_rowconfigure(0, weight=1)


    def load_categories(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        try:
            categories = self.manager.get_all_categories()
            for cat in categories:
                self.category_tree.insert("", tk.END, values=(cat.category_id, cat.name))
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load categories: {e}")

    def load_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        try:
            products = self.manager.get_all_products()
            for prod in products:
                
                formatted_price = f"₹{prod.price:.2f}"
                self.product_tree.insert("", tk.END, values=(prod.product_id, prod.name, prod.category_name, formatted_price, prod.stock_quantity))
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load products: {e}")

    def add_category(self):
        dialog = AddCategoryDialog(self, self.manager)
        if dialog.result: 
            self.load_categories() 
            self.load_products() 

    def update_category(self):
        selected_item = self.category_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a category to update.")
            return

        category_id = self.category_tree.item(selected_item, "values")[0]
        current_name = self.category_tree.item(selected_item, "values")[1]

        dialog = UpdateCategoryDialog(self, self.manager, category_id, current_name)
        if dialog.result: 
            self.load_categories() 
            self.load_products() 

    def delete_category(self):
        selected_item = self.category_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a category to delete.")
            return

        category_id = self.category_tree.item(selected_item, "values")[0]
        category_name = self.category_tree.item(selected_item, "values")[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{category_name}' (ID: {category_id})?"):
            try:
                if self.manager.delete_category(category_id):
                    messagebox.showinfo("Success", f"Category '{category_name}' deleted.")
                    self.load_categories()
                    self.load_products() 
                else:
                    messagebox.showwarning("Not Found", f"Category ID {category_id} not found.")
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Error as e:
                messagebox.showerror("Database Error", str(e))

    def add_product(self):
        categories = self.manager.get_all_categories()
        if not categories:
            messagebox.showwarning("No Categories", "Please add at least one category before adding products.")
            return

        dialog = AddProductDialog(self, self.manager, categories)
        if dialog.result: 
            self.load_products() 

    def update_product_stock(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a product to update stock.")
            return

        product_id = self.product_tree.item(selected_item, "values")[0]
        product_name = self.product_tree.item(selected_item, "values")[1]
        current_stock = self.product_tree.item(selected_item, "values")[4] 

        new_stock_str = tk.simpledialog.askstring("Update Stock", f"Enter new stock quantity for '{product_name}' (Current: {current_stock}):", parent=self)
        if new_stock_str is not None: 
            try:
                new_stock = int(new_stock_str.strip())
                if new_stock < 0:
                    messagebox.showerror("Input Error", "Stock quantity cannot be negative.", parent=self)
                    return

                if self.manager.update_product_stock(product_id, new_stock):
                    messagebox.showinfo("Success", f"Stock for '{product_name}' updated to {new_stock}.", parent=self)
                    self.load_products()
                else:
                    messagebox.showwarning("Not Found", f"Product ID {product_id} not found.", parent=self)
            except ValueError:
                messagebox.showerror("Input Error", "Invalid stock quantity. Please enter a whole number.", parent=self)
            except Error as e:
                messagebox.showerror("Database Error", str(e), parent=self)

    def delete_product(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return

        product_id = self.product_tree.item(selected_item, "values")[0]
        product_name = self.product_tree.item(selected_item, "values")[1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product '{product_name}' (ID: {product_id})?"):
            try:
                if self.manager.delete_product(product_id):
                    messagebox.showinfo("Success", f"Product '{product_name}' deleted.")
                    self.load_products()
                else:
                    messagebox.showwarning("Not Found", f"Product ID {product_id} not found.")
            except Error as e:
                messagebox.showerror("Database Error", str(e))


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()



