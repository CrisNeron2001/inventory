import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='inv_db',
        user='postgres',
        password='admin'
    )
    cursor = conn.cursor()
    
    # Eliminar todas las tablas
    cursor.execute('''
        DROP TABLE IF EXISTS role_permission CASCADE;
        DROP TABLE IF EXISTS permission CASCADE;
        DROP TABLE IF EXISTS sale CASCADE;
        DROP TABLE IF EXISTS cart_product CASCADE;
        DROP TABLE IF EXISTS cart CASCADE;
        DROP TABLE IF EXISTS user_inv CASCADE;
        DROP TABLE IF EXISTS role_inv CASCADE;
        DROP TABLE IF EXISTS product CASCADE;
        DROP TABLE IF EXISTS brand CASCADE;
        DROP TABLE IF EXISTS category CASCADE;
    ''')
    
    conn.commit()
    print('Todas las tablas han sido eliminadas correctamente')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
