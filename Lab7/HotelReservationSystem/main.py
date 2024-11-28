from db import connect_to_db
from datetime import datetime

# Function for FR1: Rooms and Rates
def get_rooms_and_rates():
    """Fetch and display room details including rates and popularity."""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to the database.")
        return
    
    cursor = conn.cursor()
    try:
        # FR1 SQL Query
        query = """
        WITH Popularity AS (
            SELECT
                r.RoomCode,
                r.RoomName,
                r.Beds,
                r.bedType,
                r.maxOcc,
                r.basePrice,
                r.decor,
                ROUND(
                    SUM(
                        CASE
                            WHEN res.CheckIn >= CURDATE() - INTERVAL 180 DAY
                              AND res.CheckOut <= CURDATE()
                            THEN DATEDIFF(res.CheckOut, res.CheckIn)
                            ELSE 0
                        END
                    ) / 180, 2
                ) AS PopularityScore
            FROM lab7_rooms r
            LEFT JOIN lab7_reservations res ON r.RoomCode = res.Room
            GROUP BY r.RoomCode, r.RoomName, r.Beds, r.bedType, r.maxOcc, r.basePrice, r.decor
        ),
        NextAvailable AS (
            SELECT
                Room AS RoomCode,
                MIN(CheckIn) AS NextAvailableCheckIn
            FROM lab7_reservations
            WHERE CheckIn > CURDATE()
            GROUP BY Room
        ),
        LastStay AS (
            SELECT
                Room AS RoomCode,
                MAX(CheckOut) AS LastCheckoutDate,
                MAX(DATEDIFF(Checkout, CheckIn)) AS LengthOfLastStay
            FROM lab7_reservations
            WHERE CheckOut < CURDATE()
            GROUP BY Room
        )
        SELECT
            p.RoomCode,
            p.RoomName,
            p.Beds,
            p.bedType,
            p.maxOcc,
            p.basePrice,
            p.decor,
            p.PopularityScore,
            na.NextAvailableCheckIn,
            ls.LengthOfLastStay,
            ls.LastCheckoutDate
        FROM Popularity p
        LEFT JOIN NextAvailable na ON p.RoomCode = na.RoomCode
        LEFT JOIN LastStay ls ON p.RoomCode = ls.RoomCode
        ORDER BY p.PopularityScore DESC;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        # Display results
        print("\nRooms and Rates:")
        print("-" * 140)
        print(f"{'RoomCode':<10} {'RoomName':<20} {'Beds':<5} {'BedType':<10} {'MaxOcc':<8} {'BasePrice':<12} {'PopularityScore':<20} {'NextCheckIn':<15} {'LastStayLength':<15} {'LastCheckout':<15}")
        print("-" * 140)
        for row in results:
            room_code = row[0]
            room_name = row[1]
            beds = row[2]
            bed_type = row[3]
            max_occ = row[4]
            base_price = f"${row[5]:.2f}"
            popularity_score = f"{row[7]:.2f}"
            next_check_in = row[8].strftime('%Y-%m-%d') if row[8] else "N/A"
            last_stay_length = str(row[9]) if row[9] else "N/A"
            last_checkout = row[10].strftime('%Y-%m-%d') if row[10] else "N/A"

            # Correctly aligned print
            print(f"{room_code:<10} {room_name:<20} {beds:<5} {bed_type:<10} {max_occ:<8} {base_price:<12} {popularity_score:<20} {next_check_in:<15} {last_stay_length:<15} {last_checkout:<15}")
        print("-" * 140)
    
    except Exception as e:
        print(f"Error while fetching rooms and rates: {e}")
    finally:
        cursor.close()
        conn.close()


# Placeholder for FR2: Reservations
def make_reservation():
    """Allow the user to make a reservation."""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        # Gather user input
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        room_code = input("Room code (or 'Any' for no preference): ").strip()
        bed_type = input("Desired bed type (or 'Any' for no preference): ").strip()
        check_in = input("Check-in date (YYYY-MM-DD): ").strip()
        check_out = input("Check-out date (YYYY-MM-DD): ").strip()
        adults = int(input("Number of adults: ").strip())
        kids = int(input("Number of kids: ").strip())
        total_guests = adults + kids

        # Validate input
        if total_guests <= 0:
            print("The total number of guests must be greater than zero.")
            return

        # Check room availability
        query = """
        SELECT RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor
        FROM lab7_rooms
        WHERE (RoomCode = %s OR %s = 'Any')
          AND (bedType = %s OR %s = 'Any')
          AND maxOcc >= %s
          AND RoomCode NOT IN (
              SELECT Room
              FROM lab7_reservations
              WHERE (CheckIn < %s AND Checkout > %s)
          )
        LIMIT 5;
        """
        cursor.execute(query, (room_code, room_code, bed_type, bed_type, total_guests, check_out, check_in))
        available_rooms = cursor.fetchall()

        # Handle no available rooms
        if not available_rooms:
            print("\nNo exact matches found. Suggesting alternatives...")
            # Suggest alternative rooms
            cursor.execute("""
            SELECT RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor
            FROM lab7_rooms
            WHERE maxOcc >= %s
            LIMIT 5;
            """, (total_guests,))
            suggestions = cursor.fetchall()
            if not suggestions:
                print("No suitable rooms are available.")
                return
            for idx, room in enumerate(suggestions, start=1):
                print(f"{idx}. {room[1]} ({room[0]}) - {room[3]} bed, Max Occupancy: {room[4]}, Price: ${room[5]:.2f}")
            return

        # Display available rooms
        print("\nAvailable Rooms:")
        for idx, room in enumerate(available_rooms, start=1):
            print(f"{idx}. {room[1]} ({room[0]}) - {room[3]} bed, Max Occupancy: {room[4]}, Price: ${room[5]:.2f}")
        
        # Prompt user to confirm
        choice = int(input("\nEnter the number of the room you'd like to book (or 0 to cancel): "))
        if choice == 0:
            print("Reservation cancelled.")
            return
        selected_room = available_rooms[choice - 1]

        # Calculate total cost (weekday and weekend rates)
        query = "SELECT DATEDIFF(%s, %s)"
        cursor.execute(query, (check_out, check_in))
        total_days = cursor.fetchone()[0]
        total_cost = total_days * float(selected_room[5])

        # Insert reservation
        insert_query = """
        INSERT INTO lab7_reservations (Room, CheckIn, Checkout, Rate, LastName, FirstName, Adults, Kids)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (selected_room[0], check_in, check_out, total_cost, last_name, first_name, adults, kids))
        conn.commit()

        print("\nReservation confirmed!")
        print(f"Name: {first_name} {last_name}")
        print(f"Room: {selected_room[1]} ({selected_room[0]})")
        print(f"Dates: {check_in} to {check_out}")
        print(f"Guests: {adults} adults, {kids} kids")
        print(f"Total cost: ${total_cost:.2f}")

    except Exception as e:
        print(f"Error while making reservation: {e}")
    finally:
        cursor.close()
        conn.close()

# Placeholder for FR3: Cancel Reservation
def cancel_reservation():
    """Allow the user to cancel an existing reservation."""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        # Prompt user for reservation code
        reservation_code = input("Enter the reservation code to cancel: ").strip()
        
        # Retrieve reservation details for confirmation
        query = """
        SELECT CODE, Room, CheckIn, Checkout, LastName, FirstName, Adults, Kids
        FROM lab7_reservations
        WHERE CODE = %s
        """
        cursor.execute(query, (reservation_code,))
        reservation = cursor.fetchone()

        if not reservation:
            print(f"No reservation found with code {reservation_code}.")
            return

        # Display reservation details
        print("\nReservation Details:")
        print(f"Code: {reservation[0]}")
        print(f"Room: {reservation[1]}")
        print(f"Check-In: {reservation[2]}")
        print(f"Check-Out: {reservation[3]}")
        print(f"Name: {reservation[5]} {reservation[4]}")
        print(f"Guests: {reservation[6]} adults, {reservation[7]} kids")

        # Confirm cancellation
        confirm = input("Are you sure you want to cancel this reservation? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Cancellation aborted.")
            return

        # Delete the reservation
        delete_query = "DELETE FROM lab7_reservations WHERE CODE = %s"
        cursor.execute(delete_query, (reservation_code,))
        conn.commit()
        print("Reservation successfully canceled.")

    except Exception as e:
        print(f"Error while canceling reservation: {e}")
    finally:
        cursor.close()
        conn.close()

# Placeholder for FR4: Search Reservations
def search_reservations():
    """Search reservations based on user input."""
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        # Collect search criteria
        first_name = input("First name (leave blank for any): ").strip()
        last_name = input("Last name (leave blank for any): ").strip()
        room_code = input("Room code (leave blank for any): ").strip()
        reservation_code = input("Reservation code (leave blank for any): ").strip()
        check_in = input("Check-in date (YYYY-MM-DD, leave blank for any): ").strip()
        check_out = input("Check-out date (YYYY-MM-DD, leave blank for any): ").strip()

        # Base query and conditions
        query = """
        SELECT r.CODE, r.Room, r.CheckIn, r.Checkout, r.LastName, r.FirstName, r.Adults, r.Kids
        FROM lab7_reservations r
        WHERE (r.FirstName LIKE %s OR %s = '')
          AND (r.LastName LIKE %s OR %s = '')
          AND (r.Room = %s OR %s = '')
          AND (r.CODE = %s OR %s = '')
        """
        params = [
            f"%{first_name}%", first_name,
            f"%{last_name}%", last_name,
            room_code, room_code,
            reservation_code, reservation_code
        ]

        # Add date range conditions if provided
        if check_in and check_out:
            query += " AND r.CheckIn >= %s AND r.CheckOut <= %s"
            params.extend([check_in, check_out])

        # Execute the query
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        # Display results
        if not results:
            print("\nNo reservations found matching the criteria.")
            return

        print("\nSearch Results:")
        print("-" * 100)
        print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<10} {:<10}".format(
            "Code", "Room", "Check-In", "Check-Out", "Name", "Adults", "Kids"
        ))
        print("-" * 100)
        for row in results:
            print("{:<10} {:<10} {:<15} {:<15} {:<15} {:<10} {:<10}".format(
                row[0], row[1], str(row[2]), str(row[3]), f"{row[5]} {row[4]}", row[6], row[7]
            ))
        print("-" * 100)

    except Exception as e:
        print(f"Error while searching reservations: {e}")
    finally:
        cursor.close()
        conn.close()


# Placeholder for FR5: Revenue Report
def generate_revenue_report():
    print("Generating Revenue Report...")
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        query = """
            WITH RevenuePerDay AS (
                SELECT
                    Room,
                    DATE(CheckIn) AS StartDate,
                    DATE(Checkout) AS EndDate,
                    Rate,
                    CASE
                        WHEN DAYOFWEEK(CheckIn) IN (1, 7) THEN Rate * 1.1 -- Weekend (Saturday, Sunday)
                        ELSE Rate
                    END AS AdjustedRatePerDay,
                    DATE_FORMAT(CheckIn, '%Y-%m') AS Month
                FROM lab7_reservations
            )
            SELECT
                Room,
                Month,
                ROUND(SUM(AdjustedRatePerDay), 2) AS TotalMonthlyRevenue
            FROM RevenuePerDay
            GROUP BY Room, Month
            ORDER BY Room, Month;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print("\nRevenue Report:")
        print("--------------------------------------------------")
        print("{:<10} {:<15} {:<10}".format("Room", "Month", "Total Revenue"))
        print("--------------------------------------------------")
        for row in results:
            print("{:<10} {:<15} ${:<10.2f}".format(row[0], row[1], row[2]))
        print("--------------------------------------------------")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


# Main Menu
def main():
    while True:
        print("\nHotel Reservation System")
        print("1. Rooms and Rates")
        print("2. Make a Reservation")
        print("3. Cancel a Reservation")
        print("4. Search Reservations")
        print("5. Revenue Report")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            get_rooms_and_rates()
        elif choice == "2":
            make_reservation()
        elif choice == "3":
            cancel_reservation()
        elif choice == "4":
            search_reservations() 
        elif choice == '5':
            generate_revenue_report()
        elif choice == "0":
            print("Exiting the system. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
