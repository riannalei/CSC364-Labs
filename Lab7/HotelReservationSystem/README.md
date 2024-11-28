# Hotel Reservation System

## How to Run
1. Install the required dependency:
- pip install mysql-connector-python

2. Set up the database:
- Use the provided SQL script to create `lab7_rooms` and `lab7_reservations` tables.
- Insert sample data for testing.

3. Run the application:
- python3 main.py

## Features Implemented
- **FR1:** Rooms and rates - Displays a sorted list of rooms with popularity and availability details.
- **FR2:** Make a reservation - Allows users to book a room based on preferences.
- **FR3:** Cancel a reservation - Cancels an existing reservation by code.
- **FR4:** Search reservations - Searches reservations based on user-specified criteria.
- **FR5:** Revenue report - Generates a monthly revenue report for each room.

## Known Issues
- The system assumes valid date formats (YYYY-MM-DD). Invalid formats may cause errors
- Minor input validation is in place; unexpected inputs may lead to undefined behavior

## Team Members
- I worked on this project individually.




