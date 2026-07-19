-- Arun Crackers POS Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS arun_crackers_pos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE arun_crackers_pos;

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    mrp DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sales table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255),
    customer_mobile VARCHAR(20),
    total_amount DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    amount_paid DECIMAL(10,2) NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0,
    payment_method VARCHAR(50),
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales items table (line items for each sale)
CREATE TABLE IF NOT EXISTS sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    mrp DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert sample products
INSERT INTO products (sku, name, description, price, cost_price, mrp, stock_quantity, category) VALUES
('001', 'Flower Pot - Special Large', 'Large flower pot crackers', 250.00, 180.00, 300.00, 50, 'Flower Pots'),
('002', 'Laxmi Bombs (28 Pcs)', 'Pack of 28 laxmi bombs', 180.00, 120.00, 180.00, 100, 'Bombs'),
('003', 'Sparklers - Multicolour 15cm', 'Multicolour sparklers, 15cm', 45.00, 25.00, 45.00, 500, 'Sparklers'),
('004', 'Chakra - 5 Inch', '5 inch chakra ground spinner', 60.00, 40.00, 75.00, 150, 'Ground Spinners'),
('005', 'Rockets - 10 Pcs', 'Pack of 10 sky rockets', 120.00, 80.00, 150.00, 80, 'Rockets');
