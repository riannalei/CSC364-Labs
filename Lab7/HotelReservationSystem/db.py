# db.py

import mysql.connector

def connect_to_db():
    try:
        print("Attempting to connect to the database...")
        conn = mysql.connector.connect(
            host="db.labthreesixfive.com",
            user="rxlei",
            password="365-fall24-028912240",
            database="rxlei",
            auth_plugin="mysql_native_password"
        )
        print("Connection successful!")
        return conn
    except mysql.connector.Error as err:
        print(f"Error code: {err.errno}")
        print(f"SQL state: {err.sqlstate}")
        print(f"Error message: {err.msg}")
        return None

def setup_tables():
    """Set up tables and populate them with sample data."""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database for table setup.")
        return

    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab7_rooms (
        RoomCode CHAR(5) PRIMARY KEY,
        RoomName VARCHAR(30) NOT NULL,
        Beds INT NOT NULL,
        bedType VARCHAR(8) NOT NULL,
        maxOcc INT NOT NULL,
        basePrice DECIMAL(6, 2) NOT NULL,
        decor VARCHAR(20) NOT NULL,
        UNIQUE (RoomName)
    );
    """)
    print("Table `lab7_rooms` created or already exists.")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab7_reservations (
        CODE INT PRIMARY KEY,
        Room CHAR(5) NOT NULL,
        CheckIn DATE NOT NULL,
        Checkout DATE NOT NULL,
        Rate DECIMAL(6, 2) NOT NULL,
        LastName VARCHAR(15) NOT NULL,
        FirstName VARCHAR(15) NOT NULL,
        Adults INT NOT NULL,
        Kids INT NOT NULL,
        FOREIGN KEY (Room) REFERENCES lab7_rooms (RoomCode)
    );
    """)
    print("Table `lab7_reservations` created or already exists.")

    # Populate tables
    cursor.execute("""
    INSERT INTO lab7_rooms (RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor)
    VALUES ('A101', 'Seaview Room', 2, 'Queen', 4, 120.00, 'Modern')
    ON DUPLICATE KEY UPDATE RoomName=RoomName;
    """)

    cursor.execute("""
    INSERT INTO lab7_reservations (CODE, Room, CheckIn, Checkout, Rate, LastName, FirstName, Adults, Kids)
    VALUES (1, 'A101', '2024-01-01', '2024-01-05', 120.00, 'Smith', 'John', 2, 0)
    ON DUPLICATE KEY UPDATE CODE=CODE;
    """)

    conn.commit()
    print("Tables set up and sample data inserted.")
    conn.close()

# Test if the file runs directly
if __name__ == "__main__":
    print("Testing db.py directly...")
    setup_tables()
