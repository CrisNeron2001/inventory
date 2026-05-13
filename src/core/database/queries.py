# ============(CREACION DE TABLA)=============>

create_category = """
	CREATE TABLE IF NOT EXISTS category (
		category_id SERIAL PRIMARY KEY,
		name VARCHAR(100) NOT NULL UNIQUE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);
"""

create_brand = """
	CREATE TABLE IF NOT EXISTS brand (
		brand_id SERIAL PRIMARY KEY,
		name VARCHAR(100) NOT NULL UNIQUE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	); 
"""

create_product = """
	CREATE TABLE IF NOT EXISTS product (
		product_id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		description TEXT NULL,
		stock INTEGER NOT NULL,
		price INTEGER NOT NULL,
        category_id INTEGER,
        brand_id INTEGER,
        sku VARCHAR(50) UNIQUE,
		category_name VARCHAR(100),
		brand_name VARCHAR(100),
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE SET NULL,
        FOREIGN KEY (brand_id) REFERENCES brand(brand_id) ON DELETE SET NULL
	);
"""

create_user_inv = """
	CREATE TABLE IF NOT EXISTS user_inv (
		user_inv_id SERIAL PRIMARY KEY,
		first_name VARCHAR(35) NOT NULL,
        middle_name VARCHAR(35) NOT NULL,
		last_name VARCHAR(35) NULL,
		rut VARCHAR(35) NOT NULL UNIQUE,
		password VARCHAR(255) NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);
"""

create_cart = """
	CREATE TABLE IF NOT EXISTS cart(
		cart_id SERIAL PRIMARY KEY,
		user_inv_id INTEGER NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (user_inv_id) REFERENCES user_inv(user_inv_id) ON DELETE CASCADE
	);
"""

create_cart_product = """
	CREATE TABLE IF NOT EXISTS cart_product(
		cart_product_id SERIAL PRIMARY KEY,
		cart_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
		quantity INTEGER NOT NULL,
		FOREIGN KEY (cart_id) REFERENCES cart(cart_id) ON DELETE CASCADE,
		FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE
	);
"""

update_cart_product_quantity = """
	UPDATE cart_product
	SET quantity = %s
	WHERE cart_id = %s AND product_id = %s
	RETURNING cart_product_id, cart_id, product_id, quantity;
"""

select_cart_product_by_cart_and_product = """
	SELECT cart_product_id, cart_id, product_id, quantity
	FROM cart_product
	WHERE cart_id = %s AND product_id = %s;
"""

create_sale = """
    CREATE TABLE IF NOT EXISTS sale (
        sale_id SERIAL PRIMARY KEY,
        cart_id INTEGER NOT NULL,
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cart_id) REFERENCES cart(cart_id) ON DELETE RESTRICT
    );
"""

# ==================(CRUD USER_INV)====================>

insert_user_inv = """
	INSERT INTO user_inv (first_name, middle_name, last_name, rut, password)
	VALUES (%s, %s, %s, %s, %s)
	RETURNING user_inv_id, first_name, middle_name, last_name, rut, created_at, updated_at;
"""

select_user_by_id = """
	SELECT 
		u.user_inv_id, 
		u.first_name, 
        u.middle_name,
		u.last_name, 
		u.rut, 
		u.created_at, 
		u.updated_at
	FROM user_inv u
	WHERE u.user_inv_id = %s;
"""

select_user_by_rut = """
	SELECT 
		u.user_inv_id, 
		u.first_name, 
        u.middle_name,
		u.last_name, 
		u.rut, 
		u.password, 
		u.created_at, 
		u.updated_at
	FROM user_inv u
	WHERE u.rut = %s;
"""

select_all_users = """
	SELECT 
		u.user_inv_id,	 
		u.first_name, 
        u.middle_name,
		u.last_name, 
		u.rut, 
		u.created_at, 
		u.updated_at
	FROM user_inv u
	ORDER BY u.rut;
"""

update_user_inv = """
	UPDATE user_inv
	SET first_name = %s, middle_name = %s, last_name = %s, rut = %s, password = %s, updated_at = CURRENT_TIMESTAMP
	WHERE user_inv_id = %s
	RETURNING user_inv_id, first_name, middle_name, last_name, rut, created_at, updated_at;
"""

delete_user_inv = """
	DELETE FROM user_inv
	WHERE user_inv_id = %s;
"""

# =============(CREACION DE INDICES)====================>

create_indexes = """
	CREATE INDEX IF NOT EXISTS idx_product_category ON product(category_id);
	CREATE INDEX IF NOT EXISTS idx_product_brand ON product(brand_id);
	CREATE INDEX IF NOT EXISTS idx_product_name ON product(name);
	CREATE INDEX IF NOT EXISTS idx_product_sku ON product(sku);
	CREATE INDEX IF NOT EXISTS idx_sale_cart ON sale(cart_id);
	CREATE INDEX IF NOT EXISTS idx_sale_date ON sale(sale_date);
	CREATE INDEX IF NOT EXISTS idx_category_name ON category(name);
	CREATE INDEX IF NOT EXISTS idx_brand_name ON brand(name);
	CREATE INDEX IF NOT EXISTS idx_userinv_rut ON user_inv(rut);
	CREATE INDEX IF NOT EXISTS idx_cart_user_inv ON cart(user_inv_id);
"""

# ==================(COMPROBAR TABLAS)==================>

checks_tables = """
	SELECT table_name 
	FROM information_schema.tables
	WHERE table_schema='public'
		AND table_name IN ('category', 'brand', 'product', 'sale', 'user_inv', 'cart', 'cart_product');
"""

# ==================(CRUD CATEGORIA)====================>

insert_category = """
	INSERT INTO category (name)
	VALUES (%s)
	RETURNING category_id, name, created_at, updated_at;
"""

select_category_name_by_id = """
	SELECT category_id, name, created_at, updated_at
	FROM category
	WHERE category_id = %s;

"""

select_all_categories_names = """
	SELECT category_id, name, created_at, updated_at
	FROM category
	ORDER BY name;
"""

update_category = """
	UPDATE category
	SET name = %s, updated_at = CURRENT_TIMESTAMP
	WHERE category_id = %s
	RETURNING category_id, name, created_at, updated_at;
"""

delete_category = """
	DELETE FROM category
	WHERE category_id = %s;
"""

# ===================(CRUD MARCA)=======================>

insert_brand = """
	INSERT INTO brand (name)
	VALUES (%s)
	RETURNING brand_id, name, created_at, updated_at;
"""

select_brand_name_by_id = """
	SELECT brand_id, name, created_at, updated_at
	FROM brand
	WHERE brand_id = %s;
"""
select_name_brand = """
	SELECT name
	FROM brand;
"""

select_all_brands_names = """
	SELECT brand_id, name, created_at, updated_at
	FROM brand
	ORDER BY name;
"""


update_brand = """
	UPDATE brand
	SET name = %s, updated_at = CURRENT_TIMESTAMP
	WHERE brand_id = %s
	RETURNING brand_id, name, created_at, updated_at;
"""

delete_brand = """
	DELETE FROM brand
	WHERE brand_id = %s;
"""

# ==================(CRUD PRODUCTO)=====================>

insert_product = """
    INSERT INTO product (
        name, 
        description, 
        stock, 
        price, 
        category_id, 
        brand_id, 
        sku,
		category_name,
		brand_name
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING 
		product_id, 
		name, 
		description, 
		stock, 
		price, 
		sku,
		created_at,
		updated_at,
		(
			SELECT 
				c.name 
			FROM category c 
			WHERE c.category_id = product.category_id
		) AS category_name,
		(
			SELECT
				b.name
			FROM brand b
			WHERE b.brand_id = product.brand_id
		) AS brand_name;
"""

select_product_by_id = """
	SELECT        
		p.product_id,
		p.name, 
		p.description, 
		p.stock, 
		p.price, 
		p.sku,
		p.created_at, 
		p.updated_at,
		c.name as category_name,
		b.name as brand_name
	FROM product p
	LEFT JOIN category c ON p.category_id = c.category_id
	LEFT JOIN brand b ON p.brand_id = b.brand_id
	WHERE p.product_id = %s;
"""

select_all_products = """
	SELECT 
		p.product_id,
		p.name,
		p.description, 
		p.stock, 
		p.price, 
		p.sku,
		p.created_at, 
		p.updated_at,
		c.name as category_name,
		b.name as brand_name
	FROM product p
	LEFT JOIN category c ON p.category_id = c.category_id
	LEFT JOIN brand b ON p.brand_id = b.brand_id
	ORDER BY p.name;
"""

update_product = """
    UPDATE product
    SET 
		name = %s, 
		description = %s, 
		stock = %s, 
		price = %s, 
        category_id = %s, 
        brand_id = %s, 
        sku = %s,
		category_name = %s,
		brand_name = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = %s
    RETURNING 
		product_id, 
		name, 
		description, 
		stock, 
		price, 
		sku,
		created_at,
		updated_at
		(
			SELECT 
				c.name 
			FROM category c 
			WHERE c.category_id = product.category_id
		) AS category_name,
		(
			SELECT
				b.name
			FROM brand b
			WHERE b.brand_id = product.brand_id
		) AS brand_name;
"""

update_product_stock_by_name = """
	UPDATE product
	SET
		stock = %s,
		updated_at = CURRENT_TIMESTAMP
	WHERE name = %s;
"""

delete_product = """
	DELETE FROM product
	WHERE product_id = %s;
"""

# ==================(CRUD VENTA)====================>

insert_sale = """
	INSERT INTO sale (cart_id)
	VALUES (%s)
	RETURNING sale_id, cart_id, sale_date, notes, created_at, updated_at;
"""

select_sale_by_id = """
	SELECT 
		s.sale_id, 
		s.cart_id,
        s.sale_date, 
        s.notes,
		s.created_at, 
		s.updated_at,
		p.name AS product_name,
		cp.quantity AS quantity,
		p.price AS unit_price,
		(cp.quantity * p.price) AS total_price
	FROM sale s
	LEFT JOIN cart_product cp ON s.cart_id = cp.cart_id
	LEFT JOIN product p ON cp.product_id = p.product_id
	WHERE s.sale_id = %s
	ORDER BY p.product_id;
"""

select_all_sales = """
	SELECT 
		s.sale_id, 
		s.cart_id,
		s.sale_date,
        s.notes,
		s.created_at, 
		s.updated_at,
		p.name AS product_name,
		cp.quantity AS quantity,
		p.price AS unit_price,
		(cp.quantity * p.price) AS total_price
	FROM sale s
	LEFT JOIN cart_product cp ON s.cart_id = cp.cart_id
	LEFT JOIN product p ON cp.product_id = p.product_id
	ORDER BY s.sale_date DESC, s.sale_id DESC, p.product_id;
"""

delete_sale = """
	DELETE FROM sale
	WHERE sale_id = %s;
"""

update_sale = """
	UPDATE sale
	SET notes = %s,
		updated_at = CURRENT_TIMESTAMP
	WHERE sale_id = %s
	RETURNING sale_id, cart_id, sale_date, notes, created_at, updated_at;
"""

# ==================(CRUD CARRITO)====================>

insert_cart = """
	INSERT INTO cart (user_inv_id)
	VALUES (%s)
	RETURNING cart_id, user_inv_id, created_at, updated_at;
"""

select_all_carts = """
	SELECT
		cp.cart_product_id,
		cp.cart_id,
		c.user_inv_id,
		p.product_id,
		p.name,
		p.price,
		cp.quantity
	FROM cart_product cp
	LEFT JOIN cart c ON cp.cart_id = c.cart_id
	LEFT JOIN user_inv u ON c.user_inv_id = u.user_inv_id
	LEFT JOIN product p ON cp.product_id = p.product_id;
"""

select_cart_by_id = """
	SELECT
		cp.cart_product_id,
		cp.cart_id,
		c.user_inv_id,
		p.product_id,
		p.name,
		p.price,
		cp.quantity
	FROM cart_product cp
	LEFT JOIN cart c ON cp.cart_id = c.cart_id
	LEFT JOIN user_inv u ON c.user_inv_id = u.user_inv_id
	LEFT JOIN product p ON cp.product_id = p.product_id
	WHERE cp.cart_id = %s;
"""

insert_cart_product = """
	INSERT INTO cart_product(cart_id, product_id, quantity)
	VALUES (%s, %s, %s)
	RETURNING cart_product_id, cart_id, product_id, quantity;
"""

remove_product_from_cart = """
	DELETE FROM cart_product
	WHERE product_id = %s AND cart_id = %s
	RETURNING cart_id, product_id, quantity;
"""

update_product_decrease_if_enough = """
	UPDATE product
	SET stock = stock - %s
	WHERE product_id = %s AND stock >= %s
	RETURNING stock;
"""
