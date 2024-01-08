# FCED-DB Project

This is a comprehensive project that involves designing a relational database, creating a Python script to clean and populate the database from a provided CSV file, and building an interactive menu-driven user interface for easy data access and manipulation. This project streamlines the management of  data, making it easier to work with the information acquired.

From the database provided (SQL file in `data` folder), we've implemented the following relational model:

Student(<u>email</u>, first_name[NN], last_name[NN], date_of_birth, gpa, state)
Course(<u>course_name</u>)
Building(<u>building_name</u>)
Exam(<u>exam_id</u>, exam_date[NN], #exam_name -> Type [NN], #course_name -> Course [NN])
Room(<u>room_name</u>, capacity, has_projector, has_computers, is_accessible, #building_name -> Building [NN])
Type(<u>exam_name</u>)
ExamAttempt(<u>#email -> Student [NN]</u>, <u>#exam_id -> Exam [NN]</u>, #room_name -> Room [NN], grade)
is_enrolled(<u>#email -> Student</u>, <u>#course_name -> Course</u>)

The UML diagram of this model in shown below.

![UML Diagram proposed](./images/uml.png?raw=true "UML")

## Members
| Name | UP Number | Main contribution |
|------|-----------|-------------------|
| Beatriz Gomes | 202300585 | Data modeling ('grades.sql'), Tabulation for menu results, Plots |
| Danillo Rodrigues | 202300683 | Data ingestion ('load_grades.py'), SQL queries for menu and interaction between menu items |
| Guilherme Soares | 202302425 | Main logic of menu and functions, user interface, integration between modules
| Mariana Lobão | 202004260 | UML diagram, Relation model, Plots |

## Usage

 1. Have  [PostgreSQL](https://www.postgresql.org/) installed either in your computer or in a cloud environment;
 2. Create a database  and using the Query Tool, run the code inside of **grades.sql**;
 3. Make sure you have all the Python requirements running `pip install -r requirements.txt` to install them all;
 4. Access your PostgreSQL database connection credentials using the Properties menu;
 5. Update the `DB_PARAMS` of the  **load_grades.py** code with them correctly. Make sure the variable `csv_file_path` contains the correct path to the `grades.csv` file. Now you can run it;
 6. Repeat step 5 with the **grades.py** file and run it. Now you can access the database interactively ;
 7. Remember to maintain all the codes in the same folder as they might import methods from each other;

## Files description
 - **uml.png** : Image of the UML Diagram this group is proposing;
 - **grades.sql** :  Create the tables and format the data accordingly to our relational model in a PostgreSQL database;
 - **load_grades.py** : Deletes all the data in the PostgreSQL database connected and rewrites it using Python;
 - **db.py** : Class representation of basic database operations using the psycopg2 package;
 - **plots.py** : All the plots functions are gathered here;
 - **grades_menu.py** :  Main code of the interactive menu;
 - **menu_functions.py** : All the SQL queries and data manipulation happens here;
