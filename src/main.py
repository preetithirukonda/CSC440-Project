import sys
import datetime
import mysql.connector


class InventoryManagementSystem:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.current_user = None
        self.current_role = None


def main():
    # Application entry point
    app = InventoryManagementSystem()
    app.run()
   

if __name__ == "__main__":
    main()