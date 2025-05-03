import mysql.connector
import os

# Database connection details - MUST MATCH XAMPP setup and app.py
# Make sure the user has privileges to CREATE DATABASE
DB_CONFIG_MYSQL = {
    'user': 'root',
    'password': '',  # Enter your XAMPP MySQL root password if set
    'host': '127.0.0.1', # Or 'localhost'
    # No 'database' key here initially, as we need to create it
}
DATABASE_NAME = 'game_review_db' # The name of the database to create/use

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(BASE_DIR, 'schema.sql')
DATA_FILE = os.path.join(BASE_DIR, 'data.sql')

def execute_sql_file(cursor, filepath):
    """ Reads and executes SQL commands from a file. """
    print(f"Executing SQL from: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Split commands based on semicolon, handling potential comments/empty lines
            sql_commands = f.read().split(';')
            for command in sql_commands:
                command = command.strip() # Remove leading/trailing whitespace
                if command and not command.startswith('--'): # Ignore empty lines and comments
                    try:
                        cursor.execute(command)
                        print(f"  Executed: {command[:50]}...") # Print start of command
                    except mysql.connector.Error as err:
                        print(f"  ERROR executing command: {command[:50]}... \n  {err}")
                        # Decide if you want to stop on error or continue
                        # raise # Uncomment to stop execution on first error
    except FileNotFoundError:
        print(f"ERROR: SQL file not found at {filepath}")
        raise
    except Exception as e:
        print(f"ERROR reading or executing file {filepath}: {e}")
        raise

def initialize_database():
    """ Connects to MySQL, creates DB, and runs schema/data SQL files. """
    connection = None # Initialize connection variable
    try:
        # 1. Connect to MySQL server (without specifying a database initially)
        print("Connecting to MySQL server...")
        connection = mysql.connector.connect(**DB_CONFIG_MYSQL)
        cursor = connection.cursor()
        print("Connected to server.")

        # 2. Create the database if it doesn't exist
        print(f"Creating database '{DATABASE_NAME}' if it doesn't exist...")
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{DATABASE_NAME}' ensured.")
        except mysql.connector.Error as err:
            print(f"ERROR creating database: {err}")
            # If DB creation fails, we probably can't continue
            raise

        # 3. Select the database to use
        cursor.execute(f"USE {DATABASE_NAME}")
        print(f"Using database '{DATABASE_NAME}'.")

        # 4. Execute schema file to create tables
        execute_sql_file(cursor, SCHEMA_FILE)
        print("Schema execution finished.")

        # 5. Execute data file to insert sample data
        execute_sql_file(cursor, DATA_FILE)
        print("Data insertion finished.")

        # 6. Commit changes
        connection.commit()
        print("Database changes committed.")

        cursor.close()

    except mysql.connector.Error as err:
        print(f"DATABASE INITIALIZATION FAILED: {err}")
    except Exception as e:
         print(f"An unexpected error occurred: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

if __name__ == '__main__':
    print("--- Starting Database Initialization ---")
    # Add confirmation step?
    # confirm = input("This will set up the database, potentially clearing existing data. Continue? (y/n): ")
    # if confirm.lower() == 'y':
    initialize_database()
    print("--- Database Initialization Complete ---")
    # else:
    #    print("Initialization cancelled.")

