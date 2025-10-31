#============(CREACION DE TABLA)=============>

create_category= """
    CREATE TABLE IF NOT EXISTS category (
        category_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

create_brand= """
    CREATE TABLE IF NOT EXISTS brand (
        brand_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ); 
"""

create_product= """
	CREATE TABLE IF NOT EXISTS product (
		product_id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		description TEXT NULL,
		quantity INTEGER NOT NULL,
		price INTEGER NOT NULL,
        category_id INTEGER,
        brand_id INTEGER,
        sku VARCHAR(50) UNIQUE,
        is_available BOOLEAN,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE SET NULL,
        FOREIGN KEY (brand_id) REFERENCES brand(brand_id) ON DELETE SET NULL
	);
"""

#=============(CREACION DE INDICES)====================>

create_indexes= """
	CREATE INDEX IF NOT EXISTS idx_product_category ON product(category_id);
	CREATE INDEX IF NOT EXISTS idx_product_brand ON product(brand_id);
	CREATE INDEX IF NOT EXISTS idx_product_name ON product(name);
	CREATE INDEX IF NOT EXISTS idx_product_sku ON product(sku);
"""

#==================(COMPROBAR TABLAS)==================>

checks_tables = """
	SELECT table_name 
	FROM information_schema.tables
	WHERE table_schema='public'
		AND table_name IN ('category', 'brand', 'product');
"""

#==================(CRUD CATEGORIA)====================>

insert_category= """
	INSERT INTO category (name)
	VALUES (%s)
	RETURNING category_id, name, created_at, updated_at;
"""

select_category_name_by_id= """
	SELECT category_id, name, created_at, updated_at
	FROM category
	WHERE category_id = %s;

"""

select_all_categories_names= """
	SELECT category_id, name, created_at, updated_at
	FROM category
	ORDER BY name;
"""

update_category= """
	UPDATE category
	SET name = %s, updated_at = CURRENT_TIMESTAMP
	WHERE category_id = %s
	RETURNING category_id, name, created_at, updated_at;
"""

delete_category= """
	DELETE FROM category
	WHERE category_id = %s;
"""

#===================(CRUD MARCA)=======================>

insert_brand= """
	INSERT INTO brand (name)
	VALUES (%s)
	RETURNING brand_id, name, created_at, updated_at;
"""

select_brand_name_by_id= """
	SELECT brand_id, name, created_at, updated_at
	FROM brand
	WHERE brand_id = %s;
"""
select_name_brand = """
	SELECT name
	FROM brand;
"""

select_all_brands_names= """
	SELECT brand_id, name, created_at, updated_at
	FROM brand
	ORDER BY name;
"""


update_brand= """
	UPDATE brand
	SET name = %s, updated_at = CURRENT_TIMESTAMP
	WHERE brand_id = %s
	RETURNING brand_id, name, created_at, updated_at;
"""

delete_brand= """
	DELETE FROM brand
	WHERE brand_id = %s;
"""

#==================(CRUD PRODUCTO)=====================>

insert_product= """
    INSERT INTO product (
        name, 
        description, 
        quantity, 
        price, 
        category_id, 
        brand_id, 
        sku,
        is_available
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING 
		product_id, 
		name, 
		description, 
		quantity, 
		price, 
		sku,
		is_available,
		created_at,
		updated_at,
		(SELECT 
			c.name 
		FROM category c 
		WHERE c.category_id = product.category_id) AS category_name,
		(SELECT
			b.name
		FROM brand b
		WHERE b.brand_id = product.brand_id) AS brand_name;
"""

select_product_by_id= """
	SELECT        
		p.product_id,
		p.name, 
		p.description, 
		p.quantity, 
		p.price, 
		p.sku,
		p.is_available,
		p.created_at, 
		p.updated_at,
		c.name as category_name,
		b.name as brand_name
	FROM product p
	LEFT JOIN category c ON p.category_id = c.category_id
	LEFT JOIN brand b ON p.brand_id = b.brand_id
	WHERE p.product_id = %s;
"""

select_all_products= """
	SELECT 
		p.product_id,
		p.name,
		p.description, 
		p.quantity, 
		p.price, 
		p.sku,
		p.is_available,
		p.created_at, 
		p.updated_at,
		c.name as category_name,
		b.name as brand_name
	FROM product p
	LEFT JOIN category c ON p.category_id = c.category_id
	LEFT JOIN brand b ON p.brand_id = b.brand_id
	ORDER BY p.name;
"""

update_product= """
    UPDATE product
    SET 
		name = %s, 
		description = %s, 
		quantity = %s, 
		price = %s, 
        category_id = %s, 
        brand_id = %s, 
        sku = %s,
        is_available = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = %s
    RETURNING 
		product_id, 
		name, 
		description, 
		quantity, 
		price, 
		sku,
		is_available,
		created_at,
		updated_at,
		(SELECT 
			c.name 
		FROM category c 
		WHERE c.category_id = product.category_id) AS category_name,
		(SELECT
			b.name
		FROM brand b
		WHERE b.brand_id = product.brand_id) AS brand_name;
"""

delete_product= """
	DELETE FROM product
	WHERE product_id = %s;
"""