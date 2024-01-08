import datetime
import psycopg2
import pandas as pd
import numpy as np
from psycopg2.extras import execute_values  

# Database connection parameters
db_params = {
    'host': 'localhost',  # Only specify the hostname or IP address
    'port': 5432,         # Specify the port separately
    'database': 'postgres',   
    'user': 'postgres', 
    'password': 'rafinha1'
}

#Specify Schema Name
schema_name = 'grades'

csv_file_path = '../data/grades.csv'
csv_data = pd.read_csv(csv_file_path)

# Define a schema dictionary where keys are column names and values are the data types
schema = {
    'exam_date': 'string' #auto converted to date when inserted in db
    ,'first_name': 'string'
    ,'last_name': 'string'
    ,'email': 'string'
    ,'date_of_birth': 'string'  #auto converted to date when inserted in db
    ,'gpa': float
    ,'course_name': 'string'
    ,'exam_name': 'string'
    ,'building_name': 'string'
    ,'room_name': 'string'
    ,'capacity': 'string' #auto converted to int when inserted in db
    ,'has_projector': 'string' #auto converted to boolean when inserted in db
    ,'has_computers': 'string' #auto converted to boolean when inserted in db
    ,'is_accessible': 'string' #auto converted to boolean when inserted in db
    ,'grade': float
    ,'state': 'string'
}

# Loop through columns and apply the data type conversion
for column, data_type in schema.items():
    csv_data[column] = csv_data[column].astype(data_type)

print(csv_data.info())

# Defining the table and their corresponding column filters
# For each table, columns need to be in the exact order that they are created in the database grades.sql script
table_configs = [
     {'table_name': 'student', 'has_id' : False, 'column_filters': ['email', 'first_name','last_name','date_of_birth','gpa','state']}
    ,{'table_name': 'course', 'has_id' : False, 'column_filters': ['course_name']}
    ,{'table_name': 'is_enrolled', 'has_id' : False, 'column_filters': ['email','course_name']}
    ,{'table_name': 'building','has_id' : False, 'column_filters': ['building_name']}
    ,{'table_name': 'room', 'has_id' : False, 'column_filters': ['room_name','capacity','has_projector','has_computers','is_accessible','building_name']}
    ,{'table_name': 'type', 'has_id' : False, 'column_filters': ['exam_name']}
    ,{'table_name': 'exam','has_id' : True, 'column_filters': ['exam_id','exam_date','course_name','exam_name']}
    ,{'table_name': 'examattempt','has_id' : False, 'column_filters': ['exam_id','room_name','email','grade'], 'reference_table': 'exam', 'referece_id_column': 'exam_id'}
]

def connect_to_database():
    try:
        conn = psycopg2.connect(
            host=db_params['host'],
            database=db_params['database'],
            user=db_params['user'],
            password=db_params['password'],
            port=db_params['port']
        )
        print(f'DATABASE CONNECTED SUCCESFULLY!')
        print()
        return conn
    except Exception as e:
        print(f"Error CONNECTING TO DATASE: {str(e)}")
        return None

def delete_data_from_table(conn, table_name, has_auto_id_column, id_column):
    try:
        cursor = conn.cursor()
        delete_query = f'DELETE FROM "{schema_name}"."{table_name}" CASCADE;'
        cursor.execute(delete_query)
        print(f'DATA DELETED SUCCESFULLY FROM "{schema_name}"."{table_name}"')
        #Reseting the id column
        if has_auto_id_column:
            reset_id_query = f"SELECT setval(pg_get_serial_sequence('{schema_name}.{table_name}', '{id_column}'), 1, false);"
            cursor.execute(reset_id_query)
            print(f'SERIAL ID RESET FOR "{schema_name}"."{table_name}"')
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f'Error DELETING TABLE "{schema_name}"."{table_name}": {str(e)}')


def insert_data_into_table(conn, table_name, data, has_auto_id_column, column_filters):
    try:
        cursor = conn.cursor()
        column_names = ', '.join(column_filters)

        if has_auto_id_column:
            column_names_without_id = ', '.join(column_filters[1:])
            insert_query = f"INSERT INTO \"{schema_name}\".\"{table_name}\" ({column_names_without_id}) VALUES %s RETURNING {column_names}"
            execute_values(cursor, insert_query, data, template=None, page_size=100)
            conn.commit()
            result = cursor.fetchall()
            print(f'DATA INSERTED SUCCESFULLY INTO "{schema_name}"."{table_name}"')
            print()
            return result
        else:
            insert_query = f"INSERT INTO \"{schema_name}\".\"{table_name}\" ({column_names}) VALUES %s"
            execute_values(cursor, insert_query, data, template=None, page_size=100)
            conn.commit()
            print(f'DATA INSERTED SUCCESFULLY INTO "{schema_name}"."{table_name}"')
            print()

    except Exception as e:
        conn.rollback()
        print(f'Error INSERTING DATA IN "{schema_name}"."{table_name}": {str(e)}')


def main():

    global csv_data 
    conn = connect_to_database()
    if not conn:
        return

    for table_config in table_configs:
        table_name = table_config['table_name']
        delete_data_from_table(conn, table_name, table_config['has_id'], table_config['column_filters'][0])  # Delete data from the table
        column_filters = table_config['column_filters']

        if table_config['has_id']:
            column_filters_without_id = table_config['column_filters'][1:] #Disconsidering the id column because it dont exist in csv
            table_data = csv_data[column_filters_without_id]
        else:    
            table_data = csv_data[column_filters]

        # Remove duplicates from the subset of columns
        table_data = table_data.drop_duplicates()

        # Convert the DataFrame to a list of tuples for insertion
        data_to_insert = [tuple(row) for row in table_data.to_records(index=False)]

        # Inserting the data
        result = insert_data_into_table(conn, table_name, data_to_insert, table_config['has_id'],column_filters)
        
        if result:
            #Result is only returning something if the table has a serial id (Check insert function - line 104)
            #We need to merge the generated IDs back to the dataset to populate tables 'exams_is_in' and 'allocation'
           
            result = tuple(
                tuple(
                    value.strftime('%Y-%m-%d') if isinstance(value, datetime.date) else str(value) #Converting 'datetime.date' back to string
                    for value in row
                )
                for row in result
            )

            data_with_serial_id = pd.DataFrame(result, columns=column_filters)

            #Joining the generated id column with original csv dataset
            csv_data_with_id = pd.merge(csv_data.copy(), data_with_serial_id, on=column_filters_without_id, how='left')

            # Replace the original csv_data with the merged dataset (with id) for the next iteration
            csv_data = csv_data_with_id.copy()

    conn.close()

if __name__ == "__main__":
    main()

