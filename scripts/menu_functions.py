def wait_enter():
    while True:
        enter = input()
        if enter == '':
            break


def top_easiest_and_hardest_courses(db,choice):
    if choice == 'e':
        order = 'DESC'
    else:
        order = ''
    query = f" SELECT * FROM(\
        	SELECT course_name, \
        		ROUND(avg(grade_c)::numeric,2) AS students_average,\
        		ROW_NUMBER() OVER (ORDER BY ROUND(avg(grade_c)::numeric,2) {order}) AS grade_rank\
        	FROM (		\
        		SELECT full_name,s.email,gpa, date_of_birth, state, course_name,\
        		ROUND(avg(COALESCE(grade,0))::numeric,2) AS grade_c\
        		FROM\
        		(\
        			SELECT *\
        			FROM grades.is_enrolled x\
        			JOIN (SELECT first_name || ' ' || last_name AS full_name, * FROM grades.student) s USING(email)\
        			JOIN (SELECT DISTINCT course_name, count(exam_name) AS n FROM grades.exam GROUP BY course_name) a USING (course_name)\
        			LEFT JOIN grades.exam USING (course_name)\
        			ORDER BY exam_id\
        		) s\
        		LEFT JOIN grades.examattempt e\
        			ON s.exam_id = e.exam_id\
        			AND s.email = e.email\
        		GROUP BY full_name,s.email,gpa, date_of_birth, state, course_name\
        		ORDER BY avg(COALESCE(grade,0)) desc \
        	)\
        	GROUP BY course_name\
        )\
        WHERE grade_rank <= 5\
        ORDER BY students_average {order};"
    
    results = db.execute_query(query)
    if choice == 'e':
        print(f"\n Top easiest courses based on average students final grades:")
    else:
        print(f"\n Top hardest courses based on average students final grades:")
    data = []
    for i, row in enumerate(results):
        course_name, grade, pos = row
        data.append([i+1, pos,course_name, grade])

    headers = ["Option","Rank Position", "Course Name", "Average Students Grade"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_students_by_course(database,results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()	


def all_students_and_grades_for_specific_exam(db, course, exam_name, exam_date):
    query = f"SELECT full_name, grade, building_name, room_name \
        FROM (SELECT first_name || ' ' || last_name AS full_name, * FROM grades.student) s \
        JOIN grades.examattempt l USING (email) \
        JOIN grades.exam x USING(exam_id) \
        JOIN grades.room r USING(room_name) \
        WHERE exam_date = '{exam_date}' \
        AND course_name = '{course}' \
        AND exam_name = '{exam_name}' \
        ORDER BY grade DESC;"
    results = db.execute_query(query)
    print(f"\n All grades and students that participated in {course} {exam_name} on {exam_date} (highest to lowest grade):")	
    data = []
    for i, row in enumerate(results):
        full_name, grade, building_name, room_name = row
        data.append([i+1, full_name, grade, f"{building_name} at {room_name}"])

    headers = ["Option","Student Name", "Grade", "Exam Location"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")
    
    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_student_by_name_or_email(database,results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()	

def exam_details_for_student_and_course(db, name, course):
    query = f" SELECT exam_date, exam_name, COALESCE(grade,0) AS grade, \
        CASE WHEN grade IS NULL THEN 'Student did not attend this exam.' \
        ELSE ' On ' || exam_date || ', at ' || building_name || ' in ' || room_name END AS location\
        FROM \
        (\
        	SELECT * \
        	FROM grades.is_enrolled x\
        	JOIN (SELECT first_name || ' ' || last_name AS full_name, * FROM grades.student) s USING(email)\
        	JOIN (SELECT DISTINCT course_name, count(exam_name) AS n FROM grades.exam GROUP BY course_name) a USING (course_name)\
        	LEFT JOIN grades.exam USING (course_name) \
        	ORDER BY exam_id\
        ) s\
        LEFT JOIN (SELECT * FROM grades.examattempt LEFT JOIN grades.room USING (room_name)) e \
        	ON s.exam_id = e.exam_id \
            AND s.email = e.email\
        WHERE full_name = '{name}'\
        AND course_name = '{course}'\
        ORDER BY exam_date;"
    results = db.execute_query(query)
    print(f"\n--{name} {course} exams detailed:")	
    data = []
    for i, row in enumerate(results):
        exam_date,exam_name, grade, location = row
        data.append([i+1, exam_name, location, grade])

    headers = ["Option", "Exam name", "Location", "Grade"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")
    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            all_students_and_grades_for_specific_exam(database,course,results[detail_response][1],results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()	


def top_students_by_gpa(db):
    query = "SELECT DENSE_RANK() OVER (ORDER BY gpa DESC) AS placement_order, \
        first_name || ' ' || last_name AS full_name, gpa \
        FROM grades.student s1 \
        WHERE \
        	(SELECT COUNT(DISTINCT gpa) FROM grades.student s2 WHERE s2.gpa > s1.gpa) < 5 \
        ORDER BY gpa DESC;"
    results = db.execute_query(query)
    print("\n Top 5 Students by GPA:")
    data = []
    for i, row in enumerate(results):
        pos, student_full_name, gpa = row
        data.append([i+1, pos, f"{student_full_name} ",  gpa])

    headers = ["Option","Rank Position", "Student Name", "GPA"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_student_by_name_or_email(database,results[detail_response][1])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def top_students_by_course(db, course_name):
    query = f"WITH RankedGrades AS (\
                SELECT full_name, \
                       ROUND(avg(COALESCE(grade, 0))::numeric, 2) AS grade_c,\
                       ROW_NUMBER() OVER (ORDER BY avg(COALESCE(grade, 0)) DESC) AS grade_rank\
                FROM (\
                    SELECT *\
                    FROM grades.is_enrolled x\
                    JOIN (\
                        SELECT first_name || ' ' || last_name AS full_name, * FROM grades.student\
                    ) s USING(email)\
                    JOIN (\
                        SELECT DISTINCT course_name, count(exam_name) AS n FROM grades.exam GROUP BY course_name\
                    ) a USING (course_name)\
                    LEFT JOIN grades.exam USING (course_name)\
                    ORDER BY exam_id\
                ) s\
                LEFT JOIN (\
                    SELECT * FROM grades.examattempt\
                    LEFT JOIN grades.room USING (room_name)\
                ) e ON s.exam_id = e.exam_id AND s.email = e.email\
                WHERE course_name = '{course_name}'\
                GROUP BY full_name\
            )\
            SELECT grade_rank, full_name, grade_c\
            FROM RankedGrades\
            WHERE grade_rank <= 5\
            ORDER BY grade_rank;"
    results = db.execute_query(query)

    if len(results) == 0:
        print('The course you tried to search doesn\'t exist in our database. Press Enter to return to the menu.')
        wait_enter()
        return

    print(f"Top 5 Students in '{course_name}' by Grade:")

    data = []
    for i, row in enumerate(results):
        pos, student_full_name, final_grade = row
        data.append([i+1, pos, f"{student_full_name} ",  final_grade])

    headers = ["Option","Rank Position", "Student Name", "Final Grade"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            exam_details_for_student_and_course(database,results[detail_response][1],course_name)
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def top_courses_by_enrollments(db):
    query = "SELECT DENSE_RANK() OVER (ORDER BY COUNT(email) DESC) AS placement_order, \
            course_name, COUNT(email) AS total_students \
            FROM grades.is_enrolled \
            GROUP BY course_name \
            HAVING COUNT(email) IN ( \
                SELECT DISTINCT COUNT(email) AS total_students \
                FROM grades.is_enrolled \
                GROUP BY course_name \
                ORDER BY COUNT(email) DESC \
                LIMIT 3 \
            ) \
            ORDER BY COUNT(email) DESC"

    results = db.execute_query(query)

    print("Top Courses by Enrolled Students:")
    data = []
    for i,row in enumerate(results):
        pos, course_name, num_enrolled_students = row
        data.append([i+1,pos, f"{course_name}",  num_enrolled_students])

    headers = ["Option","Rank Position", "Course Name", "Nummber enrolled students"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_students_by_course(database,results[detail_response][1])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()	

def search_student_by_name_or_email(db, name):
    if '@jsuniversity.edu' in name:
        where_filter = f"s.email = '{name}'"
    else:
        where_filter = f"full_name = '{name}'"
        
    query = f"SELECT full_name,s.email,gpa, date_of_birth, state, course_name,\
            ROUND(avg(COALESCE(grade,0))::numeric,2) AS grade_c \
            FROM \
            (\
            	SELECT * \
            	FROM grades.is_enrolled x\
            	JOIN (SELECT first_name || ' ' || last_name AS full_name, * FROM grades.student) s USING(email)\
            	JOIN (SELECT DISTINCT course_name, count(exam_name) AS n FROM grades.exam GROUP BY course_name) a USING (course_name)\
            	LEFT JOIN grades.exam USING (course_name) \
            	ORDER BY exam_id\
            ) s\
            LEFT JOIN grades.examattempt e \
            	ON s.exam_id = e.exam_id \
            	AND s.email = e.email\
            WHERE {where_filter}\
            GROUP BY full_name,s.email,gpa, date_of_birth, state, course_name\
            ORDER BY avg(COALESCE(grade,0)) desc;"
    results = db.execute_query(query)

    print(f"\n-----------------------------------------------------\n"
          f"Transcript of Records for {name}:\n"
          f"-----------------------------------------------------")
    data = []
    for i, row in enumerate(results):
        full_name,email,gpa, date_of_birth, state, course_name, avg_grade= row
        data.append([i+1, course_name, avg_grade])

    print(f"\nFull Name: {full_name} , Email: {email} \n"
          f"Birth Date (Y-M-D): {date_of_birth} , State: {state} \n"
          f"GPA: {gpa} \n"
          f"Courses and Final Grades (highest to lowest): \n"
          f"P.S.: Calculated with simple avarage, based on all exams conducted by the course.")    
    print(tabulate(data, headers=["Option", "Course Name", "Average Grade"], tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            exam_details_for_student_and_course(database,full_name,results[detail_response][5])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_students_by_age(db, age_interval):
    query = f"SELECT first_name || ' ' || last_name AS full_name, \
            age, date_of_birth, gpa, email \
            FROM (SELECT EXTRACT(YEAR FROM age(current_date, date_of_birth)) AS age, * FROM grades.student) b \
            WHERE age {age_interval}"
    results = db.execute_query(query)

    print(f"Students with age {age_interval}:")
    data = []
    for i, row in enumerate(results):
        full_name, age, birthdate, gpa, email = row
        data.append([i+1,f"{full_name}", gpa, f"{email}", age, birthdate])

    headers = ["Option","Full Name", "GPA", "Email", "Age", "Birth Date"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_student_by_name_or_email(database,results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_students_by_gpa(db, gpa_interval):
    query = f"SELECT first_name || ' ' || last_name AS full_name, gpa, email \
            FROM grades.student \
            WHERE gpa {gpa_interval}"
    results = db.execute_query(query)

    print(f"Students with gpa {gpa_interval}:")
    data = []
    for i,row in enumerate(results):
        full_name, gpa, email = row
        data.append([i+1,f"{full_name}", f"{email}", gpa])

    headers = ["Option", "Student Name", "Email", "GPA"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_student_by_name_or_email(database,results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_students_by_course(db, course_name):
    query = f"SELECT full_name,\
		ROUND(avg(COALESCE(grade,0))::numeric,2) AS grade_c\
		FROM(\
			SELECT *\
			FROM grades.is_enrolled x\
			JOIN (SELECT first_name || ' ' || last_name AS full_name, * FROM grades.student) s USING(email)\
			JOIN (SELECT DISTINCT course_name, count(exam_name) AS n FROM grades.exam GROUP BY course_name) a USING (course_name)\
			LEFT JOIN grades.exam USING (course_name)\
			ORDER BY exam_id\
		) s\
		LEFT JOIN grades.examattempt e\
			ON s.exam_id = e.exam_id\
			AND s.email = e.email\
		WHERE course_name = '{course_name}'\
		GROUP BY full_name,s.email,gpa, date_of_birth, state, course_name\
		ORDER BY avg(COALESCE(grade,0)) desc;"	
    results = db.execute_query(query)

    print(f"Students enrolled in {course_name} classes:")
    data = []
    for i, row in enumerate(results):
        full_name, grade = row
        data.append([i+1,full_name, grade])

    headers = ["Option", "Full Name", "Final Grade"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")
    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            exam_details_for_student_and_course(database,results[detail_response][0],course_name)
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def list_exams_by_course(db, course_name):
    query = f"SELECT exam_date, exam_name, building_name, string_agg(room_name, ', ') AS rooms \
            FROM grades.exam \
            JOIN (SELECT DISTINCT room_name, exam_id FROM grades.examattempt) USING (exam_id) \
            JOIN grades.room USING(room_name) \
            WHERE course_name = '{course_name}' \
            GROUP BY building_name,exam_id \
            ORDER BY exam_date;"
    results = db.execute_query(query)

    print(f"All {course_name} exams:")
    data = []
    for i,row in enumerate(results):
        date, name, building, room = row
        room_list = " and".join(room.split(',')) if ',' in room else room
        data.append([i+1, f"{name}",  f"in {room_list} at the {building}", date])

    headers = ["Option","Exam Name", "Room and Building", "Date (Y-M-D)"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            all_students_and_grades_for_specific_exam(database,course_name,results[detail_response][1],results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()	

def search_exams_by_student_name_or_email(db, name):
    if '@jsuniversity.edu' in name:
        where_filter = f"s.email = '{name}'"
    else:
        where_filter = f"full_name = '{name}'"

    query = f"SELECT exam_date, course_name, exam_name, building_name, room_name, grade \
        FROM (SELECT first_name || ' ' || last_name AS full_name, * FROM grades.student) s \
        JOIN grades.examattempt l USING (email) \
        JOIN grades.exam x USING(exam_id) \
        JOIN grades.room r USING(room_name) \
        WHERE {where_filter} \
        ORDER BY exam_date"
    results = db.execute_query(query)

    print(f"\n Exams where {name} attended (cronological order):")
    data = []
    for i, row in enumerate(results):
        date, course_name, exam_name, building, room, grade = row
        data.append([i+1, f"{exam_name}", f"{course_name}", f"{room} at {building}", date, grade])

    headers = ["Option","Exam", "Course", "Room and Building", "Date (Y-M-D)", "Grade"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")
    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            all_students_and_grades_for_specific_exam(database,results[detail_response][1],results[detail_response][2],results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_exams_by_type(db, chosen_type):
    types = {
        1: 'Quiz 1',
        2: 'Midterm Exam',
        3: 'Final Exam',
        4: 'Fitness Test',
        5: 'Project Presentation',
        6: 'Term Paper',
        7: 'Debate',
    }
    query = f"SELECT exam_date, course_name,  building_name, string_agg(room_name, ', ') AS rooms \
            FROM grades.exam \
            JOIN (SELECT DISTINCT room_name, exam_id FROM grades.examattempt) USING (exam_id) \
            JOIN grades.room USING(room_name) \
            WHERE exam_name = '{types[chosen_type]}' \
            GROUP BY building_name, exam_id \
            ORDER BY exam_date;"
    results = db.execute_query(query)

    print(f"{types[chosen_type]}'s that are scheduled:")
    data = []
    for i, row in enumerate(results):
        date, course_name, building, room = row
        room_list = " and".join(room.split(',')) if ',' in room else room
        data.append([i+1, f"{course_name}", f"In {room_list} at the {building}", date])

    headers = ["Option","Course", "Room and Building", "Date (Y-M-D)"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            all_students_and_grades_for_specific_exam(database,results[detail_response][1],types[chosen_type],results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_exams_by_building(db, chosen_type):
    types = {
        1: 'Main Building',
        2: 'Science Building',
        3: 'Arts Building',
        4: 'Engineering Building',
        5: 'Library',
    }
    query = f"SELECT exam_date,exam_name, course_name, string_agg(room_name, ', ') AS rooms \
            FROM grades.exam \
            JOIN (SELECT DISTINCT room_name, exam_id FROM grades.examattempt) USING (exam_id) \
            JOIN grades.room USING(room_name) \
            WHERE building_name = '{types[chosen_type]}' \
            GROUP BY building_name, exam_id \
            ORDER BY exam_date;"
    results = db.execute_query(query)

    print(f"The exams that are scheduled to happen in the {types[chosen_type]} are:")
    data = []
    for i, row in enumerate(results):
        date, exam_name, course_name,  room = row
        data.append([i+1, f"{exam_name}", f"{course_name}", f"{room}", date])

    headers = ["Option","Exam", "Course", "Room", "Date (Y-M-D)"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            all_students_and_grades_for_specific_exam(database,results[detail_response][2],results[detail_response][1],results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_room_with_projector(db):
    query = f"SELECT building_name, room_name, capacity, \
            CASE WHEN has_computers IS TRUE THEN 'Yes' ELSE 'No' END AS has_computers, \
            CASE WHEN is_accessible IS TRUE THEN 'Yes' ELSE 'No' END AS is_accessible FROM grades.room \
            WHERE has_projector IS TRUE \
            ORDER BY building_name, capacity"
    results = db.execute_query(query)

    print(f"The rooms with projectors are:")
    data = []
    for i,row in enumerate(results):
        building, room, capacity, computers, accessibility = row
        data.append([i+1,f"{room} at {building}", capacity, f"{computers}",  f"{accessibility}"])

    headers = ["Option","Room and Building", "Capacity", "Computers", "Accessibility"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")
    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_exams_in_room(db, results[detail_response][1].split(' ')[1])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_room_with_computer(db):
    query = f"SELECT building_name, room_name, capacity, \
            CASE WHEN has_projector IS TRUE THEN 'Yes' ELSE 'No' END AS has_projector, \
            CASE WHEN is_accessible IS TRUE THEN 'Yes' ELSE 'No' END AS is_accessible FROM grades.room \
            WHERE has_computers IS TRUE \
            ORDER BY building_name, capacity"
    results = db.execute_query(query)

    print(f"The rooms with computers are:")
    data = []
    for i,row in enumerate(results):
        building, room, capacity, projectors, accessibility = row
        data.append([i+1,f"{room} at {building}", capacity, f"{projectors}", f"{accessibility}"])

    headers = ["Option","Room and Building", "Capacity", "Projectors", "Accessibility"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_exams_in_room(db, results[detail_response][1].split(' ')[1])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_room_by_capacity(db):
    query = f"SELECT  capacity, building_name, room_name, \
            CASE WHEN has_projector IS TRUE THEN 'Yes' ELSE 'No' END AS has_projector, \
            CASE WHEN has_computers IS TRUE THEN 'Yes' ELSE 'No' END AS has_computers, \
            CASE WHEN is_accessible IS TRUE THEN 'Yes' ELSE 'No' END AS is_accessible FROM grades.room \
            ORDER BY capacity DESC"
    results = db.execute_query(query)

    print(f"The rooms ordered by capacity are:")
    data = []
    for i,row in enumerate(results):
        capacity, building, room, projectors, computers, accessibility = row
        data.append([i+1, f"{room} at {building}", capacity, f"{projectors}", f"{computers}", f"{accessibility}"])

    headers = ["Option","Room and Building", "Capacity", "Projectors", "Computers", "Accessibility"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")

    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            search_exams_in_room(db, results[detail_response][2].split(' ')[1])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def search_exams_in_room(db, room_number):
    query = f"SELECT exam_date,exam_name, course_name \
            FROM grades.exam \
            JOIN (SELECT DISTINCT room_name, exam_id FROM grades.examattempt) USING (exam_id) \
            JOIN grades.room USING(room_name) \
            WHERE room_name = 'Room {room_number}' \
            ORDER BY exam_date;"
    results = db.execute_query(query)

    print(f"The exams scheduled for the Room {room_number} are:")
    data = []
    for i,row in enumerate(results):
        date, exam_name, course_name = row
        data.append([i+1, f"{exam_name}", f"{course_name}",  f"{date}"])

    headers = ["Option", "Exam Name", "Course Name", "Date (Y-M-D)"]
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    
    detail_response = input('Enter option number to see details or 0 to go back to menu: ')
    while True:
        try:
            detail_response = int(detail_response)
            break
        except ValueError:
            detail_response = input("Invalid choice. Enter a valid option:")
    if detail_response == 0:
        return
    else:
        detail_response = detail_response - 1 
        if detail_response in (range(len(results))):
            all_students_and_grades_for_specific_exam(database,results[detail_response][2],results[detail_response][1],results[detail_response][0])
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()