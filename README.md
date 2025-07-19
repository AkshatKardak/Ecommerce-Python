## E-commerce Inventory Manager

This is a desktop application built with Python and Tkinter for managing product categories and products in an e-commerce inventory. It connects to a **(MySQL Server Command Line Prompt)** database to store and retrieve data, providing a user-friendly graphical interface for common inventory management tasks.

---

## Features
- Category Management:
- Add new product categories.
- View all existing categories.
- Update category names.
- Delete categories (only if no products are associated with them).
- Product Management:
- Add new products with details like name, description, price, stock quantity, and category.
- View all products with their associated category names.
- Update product stock quantities.
- Delete products.
- Database Integration: Seamlessly interacts with a MySQL database to persist inventory data.
- User-Friendly GUI: Intuitive interface built with Tkinter for easy navigation and operations.
- Refresh Data: The category and product lists automatically refresh after successful additions, updates, or deletions.

--- 

## Screenshots
- `Main UI.png`

---

## Technologies Used
- Python 
- Tkinter (for GUI)
- MySql Command Line Prompt (for MySQL database interaction)

---

## Setup and Installation
- Install Python Extensions on Vs code 
- pip install tkinter
- pip install mysql-connector-python
- Create the Database named ecommerce_db 


---

## SQL
CREATE DATABASE ecommerce_db;
USE ecommerce_db;

b. Create Tables
The application expects categories and products tables. Execute the following SQL commands to create them:

---

## Create categories table

CREATE TABLE categories (
 - category_id INT AUTO_INCREMENT PRIMARY KEY,
  - name VARCHAR(255) NOT NULL UNIQUE
)

---

## Create products table
CREATE TABLE products (
- product_id INT AUTO_INCREMENT PRIMARY KEY,
- name VARCHAR(255) NOT NULL UNIQUE,
-  description TEXT,
- price DECIMAL(10, 2) NOT NULL,
-  stock_quantity INT NOT NULL,
- category_id INT,
- FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

---

## Database Configuration
DB_CONFIG = {
  -  'host': 'localhost',
  - 'database': 'ecommerce_db', # Ensure this matches your database name
  - 'user': 'root',             # Your MySQL username
  -  'password': 'Akshat9091'    # Your MySQL password
}

---

## Installation
Clone the Repository:
```sh
git clone https://github.com/AkshatKardak/Ecommerce-Python.git
cd Ecommerce-Python
```

---

## Contributors
Akshat Kardak - GitHub Profile **"https://github.com/AkshatKardak"**
