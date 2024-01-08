import psycopg2
import sys
import pandas as pd
from typing import List, Optional, Tuple

class DB:
    def __init__(
        self,
        database: str,
        user: str,
        password: str,
        schema: str,
        host: str = "dbm.fe.up.pt",
        port: str = "5433"        
    ) -> None:
        """
            Initialize a DatabaseConnection object and establish a database connection.

            Args:
                database (str): The name of the PostgreSQL database.
                user (str): The username for connecting to the database.
                password (str): The password for connecting to the database.
                schema (str): The schema to be used.
                host (str, optional): The host address of the database (default is "dbm.fe.up.pt").
                port (str, optional): The port number for the database connection (default is "5433").
        """
        try:
            self.connection = psycopg2.connect(
                database=database,
                user=user,
                password=password,
                host=host,
                port=port,
                options=f'-c search_path={schema}'
            )
            self.cursor = self.connection.cursor()
            print("Connected to the database.")
        except psycopg2.Error as e:
            print("Error connecting to the database:", e)
            sys.exit(1)

    def __del__(self) -> None:
        """
            Destructor method to close the database connection and cursor when the object is destroyed.
        """
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()
    
    
    def execute_query(self, query: str) -> Optional[List[Tuple]]:
        """
            Execute a SQL query and return the results.

            Args:
                query (str): The SQL query to execute.

            Returns:
                Optional[List[Tuple]]: A list of tuples containing the query results, or None if there's an error.
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print("Error executing query:", e)
            return None
    
    def clear_database(self) -> None:
        """
            Clear the database by dropping all tables, leaving only the schema structure intact.
            WARNING: This method will permanently delete all tables and their data.
        """
        try:
            self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = self.cursor.fetchall()
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"DROP TABLE {table_name} CASCADE;")
            
            self.connection.commit()
            print("Database cleared successfully. Tables dropped.")
        except psycopg2.Error as e:
            self.connection.rollback()
            print("Error clearing the database:", e)

    def populate_from_csv(self, csv_file_path):
        """
        Create tables and populate them with data from a CSV file.

        Args:
            csv_file_path (str): The path to the CSV file.
        """
        try:
            df = pd.read_csv(csv_file_path)
            table_names = df.columns.tolist()

            for table_name in table_names:
                columns = df[table_name].columns
                column_definitions = [
                    psycopg2.sql.Identifier(col).as_string(self.cursor)
                    + " VARCHAR(255)"
                    for col in columns
                ]

                create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"

                self.cursor.execute(create_table_query)
                self.connection.commit()

                table_df = df[table_name]
                for _, row in table_df.iterrows():
                    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))});"
                    self.cursor.execute(insert_query, tuple(row))
                    self.connection.commit()

                print(f"Table {table_name} created and populated with data.")
        except psycopg2.Error as e:
            print("Error:", e)