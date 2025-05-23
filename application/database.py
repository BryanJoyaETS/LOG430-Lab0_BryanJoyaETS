import psycopg2
from psycopg2 import pool

# Database configuration
DB_CONFIG = {
    "host": "db",
    "database": "mydatabase",
    "user": "myuser",
    "password": "mypassword"
}

# Create a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)

def create_connection():
    print("Creating a new connection")
    return connection_pool.getconn()

def setup_database():
    conn = create_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS produit (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    categorie VARCHAR(255),
                    stock INTEGER NOT NULL,
                    prix DECIMAL(10, 2) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vente (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ligne_vente (
                    id SERIAL PRIMARY KEY,
                    vente_id INTEGER REFERENCES vente(id),
                    produit_id INTEGER REFERENCES produit(id),
                    quantite INTEGER NOT NULL,
                    prix_unitaire DECIMAL(10, 2) NOT NULL
                )
            """)
            conn.commit()
    except psycopg2.Error as e:
        print(f"Error setting up database: {e}")
    finally:
        connection_pool.putconn(conn)

def clear_and_populate_produit():
    conn = create_connection()
    try:
        with conn.cursor() as cur:
            print("Dropping existing tables...")
            cur.execute("DROP TABLE IF EXISTS ligne_vente CASCADE;")
            cur.execute("DROP TABLE IF EXISTS vente CASCADE;")
            cur.execute("DROP TABLE IF EXISTS produit CASCADE;")
            print("Tables dropped.")

            print("Recreating tables...")
            cur.execute("""
                CREATE TABLE produit (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    categorie VARCHAR(255),
                    stock INTEGER NOT NULL,
                    prix DECIMAL(10, 2) NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE vente (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE ligne_vente (
                    id SERIAL PRIMARY KEY,
                    vente_id INTEGER REFERENCES vente(id),
                    produit_id INTEGER REFERENCES produit(id),
                    quantite INTEGER NOT NULL,
                    prix_unitaire DECIMAL(10, 2) NOT NULL
                )
            """)
            print("Tables created.")

            print("Inserting initial entries into produit table...")
            cur.execute("""
                INSERT INTO produit (nom, categorie, stock, prix) VALUES
                ('Product1', 'Category1', 100, 10.99),
                ('Product2', 'Category2', 200, 20.99),
                ('Product3', 'Category3', 150, 15.99),
                ('Product4', 'Category4', 300, 30.99),
                ('Product5', 'Category5', 250, 25.99);
            """)
            conn.commit()
            print("Produit table populated successfully.")
    except psycopg2.Error as e:
        print(f"Error resetting and populating database: {e}")
        conn.rollback()
    finally:
        if conn:
            connection_pool.putconn(conn)
