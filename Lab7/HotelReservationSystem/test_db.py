from db import connect_to_db, setup_tables

# Test the database connection
conn = connect_to_db()
if conn:
    print("Database connection successful!")
    conn.close()
else:
    print("Database connection failed.")

# Test table setup
setup_tables()
