import os
from scripts.db import DB
from typing import List, Tuple, Dict, Union
from tabulate import tabulate
from plots import *
from menu_functions import *

DB_PARAMS: Dict[str, Union[str, int]] = {
    'host': 'localhost',
    'port': 5432,
    'database': 'fced',
    'user': 'postgres',
    'password': 'admin'
}

SCHEMA_NAME = 'grades'
database = DB(
    host=DB_PARAMS['host'],
    database=DB_PARAMS['database'],
    user=DB_PARAMS['user'],
    password=DB_PARAMS['password'],
    port=DB_PARAMS['port'],
    schema=SCHEMA_NAME
)

MENU = {
    1: {
        'title': 'Rankings',
        'options': {
            1: {
                'title': 'Top 05 students by GPA',
                'options': {},
                'function': top_students_by_gpa,
            },
            2: {
                'title': 'Top 05 students by Course',
                'options': {
                    1: {
                        'title': 'Specify course name',
                        'options': {},
                        'function': top_students_by_course,
                    },
                },
            },
            3: {
                'title': 'Top 05 easiest courses (based on exam grades)',
                'options': {},
                'function': top_easiest_and_hardest_courses,
            },
            4: {
                'title': 'Top 05 hardest courses (based on exam grades)',
                'options': {},
                'function': top_easiest_and_hardest_courses,
            }, 
            5: {
                'title': 'Top 03 courses by Enrollments',
                'options': {},
                'function': top_courses_by_enrollments,
            },
            6: 'Back to Main Menu',
        }
    },
    2: {
        'title': 'Students',
        'options': {
            1: {
                'title': 'Search student',
                'options': {
                    1: {
                        'title': 'Specify full name (i.e.: Ava Lopez)',
                        'options': {},
                        'function': search_student_by_name_or_email,
                    },
                    2: {
                        'title': 'Specify email (i.e.: chloe.perez@jsuniversity.edu)',
                        'options': {},
                        'function': search_student_by_name_or_email,
                    },
                }
            },         
            2: {
                'title': 'Filter students by age',
                'options': {
                    1: {
                        'title': 'Specify Age (Use <, <=, >, >=, =, !=)',
                        'options': {},
                        'function': search_students_by_age,
                    },
                }
            },            
            3: {
                'title': 'Filter students by GPA',
                'options': {
                    1: {
                        'title': 'Specify GPA (Use <, <=, >, >=, =, !=)',
                        'options': {},
                        'function': search_students_by_gpa,
                    },
                }
            },
            4: 'Back to Main Menu',
        }
    },
    3: {
        'title': 'Courses',
        'options': {
            1: {
                'title': 'See all enrolled students and their respective grades by Course',
                'options': {
                    1: {
                        'title': 'Specify Course name',
                        'options': {},
                        'function': search_students_by_course,
                    },
                }
            },
            2: {
                'title': 'Check the exams of a course',
                'options': {
                    1: {
                        'title': 'Specify Course name',
                        'options': {},
                        'function': list_exams_by_course,
                    },
                }
            },
            3: 'Back to Main Menu',
        }
    },
    4: {
        'title': 'Exams',
        'options': {
            1: {
                'title': 'Search exams by student',
                'options': {
                    1: {
                        'title': 'Specify full name (i.e.: Ava Lopez)',
                        'options': {},
                        'function': search_exams_by_student_name_or_email,
                    },
                    2: {
                        'title': 'Specify email (i.e.: chloe.perez@jsuniversity.edu)',
                        'options': {},
                        'function': search_exams_by_student_name_or_email,
                    },
                }
            },
            2: {
                'title': 'Search exams by course',
                'options': {
                    1: {
                        'title': 'Specify Course',
                        'options': {},
                        'function': list_exams_by_course,
                    },
                }
            },
            3: {
                'title': 'Search exams by type',
                'options': {
                    1: {
                        'title': 'Quiz 1',
                        'options': {},
                        'function': search_exams_by_type,
                    },
                    2: {
                        'title': 'Midterm Exam',
                        'options': {},
                        'function': search_exams_by_type,
                    },
                    3: {
                        'title': 'Final Exam',
                        'options': {},
                        'function': search_exams_by_type,
                    },
                    4: {
                        'title': 'Fitness Test',
                        'options': {},
                        'function': search_exams_by_type,
                    },
                    5: {
                        'title': 'Project Presentation',
                        'options': {},
                        'function': search_exams_by_type,
                    },
                    6: {
                        'title': 'Term Paper',
                        'options': {},
                        'function': search_exams_by_type,
                    },
                    7: {
                        'title': 'Debate',
                        'options': {},
                        'function': search_exams_by_type,
                    },
                }
            },
            4: {
                'title': 'Search exams by building',
                'options': {
                    1: {
                        'title': 'Main Building',
                        'options': {},
                        'function': search_exams_by_building,
                    },
                    2: {
                        'title': 'Science Building',
                        'options': {},
                        'function': search_exams_by_building,
                    },
                    3: {
                        'title': 'Arts Building',
                        'options': {},
                        'function': search_exams_by_building,
                    },
                    4: {
                        'title': 'Engineering Building',
                        'options': {},
                        'function': search_exams_by_building,
                    },
                    5: {
                        'title': 'Library',
                        'options': {},
                        'function': search_exams_by_building,
                    },
                }
            },
            5: 'Back to Main Menu',
        }
    },
    5: {
        'title': 'Rooms',
        'options': {
            1: {
                'title': 'Search Rooms',
                'options': {
                    1: {
                        'title': 'With projector',
                        'options': {},
                        'function': search_room_with_projector,
                    },
                    2: {
                        'title': 'With computer',
                        'options': {},
                        'function': search_room_with_computer,
                    },
                    3: {
                        'title': 'See all rooms',
                        'options': {},
                        'function': search_room_by_capacity,
                    },
                }
            },
            2: {
                'title': 'See all exams for a specific room',
                'options': {
                    1: {
                        'title': 'Specify only room number (i.e.: 901, A01, 101)',
                        'options': {},
                        'function': search_exams_in_room,
                    },
                }
            },
            3: 'Back to Main Menu',
        }
    },
    6: {
        'title': 'Plots (figures will open in new window)',
        'options': {
            1: {
                'title': 'GPA Distribution',
                'options': {},
                'function': gpa_distribuition_plot,
            },
            2: {
                'title': 'Number of Students Doing an Exam per Date',
                'options': {},
                'function': number_of_students_in_exam_per_date_plot,
            },
            3: {
                'title': 'Number of Courses per Building',
                'options': {},
                'function': number_of_courses_per_building_plot,
            },
            4: {
                'title': 'Number of Exams per Room',
                'options': {},
                'function': students_per_exam_per_room_plot,
            },
            5: {
                'title': 'Number of Rooms per Building',
                'options': {},
                'function': number_of_rooms_per_building_plot,
            },
            6: {
                'title': 'Exam grades distribution per Course',
                'options': {},
                'function': exam_grade_distribution_per_course,
            },
            7: {
                'title': 'Number of students per State',
                'options': {},
                'function': number_of_students_per_state,
            },
            8: {
                'title': 'Age distribution of best students by course',
                'options': {},
                'function': age_distribution_best_students_by_course,
            },
            9: 'Back to Main Menu',
        }
    },
    7: {
        'title': 'Exit',
    }
}


def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_menu_options(options):
    for option, info in options.items():
        if isinstance(info, dict):
            print(f"{option}: {info['title']}")
        elif isinstance(info, str) and info == 'Back to Main Menu':
            print(f"{option}: {info}")

def handle_menu(menu, menu_id):
    while True:
        clear_screen()
        print(menu[menu_id]['title'])
        display_menu_options(menu[menu_id]['options'])
        choice = input("Enter your choice (1-{}): ".format(len(menu[menu_id]['options'])))

        if choice == str(len(menu[menu_id]['options'])):
            return
        try:
            choice = int(choice)
        except:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()
            return

        if choice in menu[menu_id]['options']:
            if isinstance(menu[menu_id]['options'][choice], dict):
                function_info = menu[menu_id]['options'][choice]
                if not function_info['options']:
                    if function_info['function'] == top_easiest_and_hardest_courses:
                        if choice == 3:
                            clear_screen()
                            function_info['function'](database, 'e')
                        else:
                            clear_screen()
                            function_info['function'](database, 'h')
                    else:
                        clear_screen()
                        function_info['function'](database)
                else:
                    if len(menu[menu_id]['options'][choice]['options']) == 1:
                        display = menu[menu_id]['options'][choice]['options'][1]['title']
                        user_input = input(f"{display}: ")
                        clear_screen()
                        menu[menu_id]['options'][choice]['options'][1]['function'](database, user_input)
                    else:
                        display_menu_options(menu[menu_id]['options'][choice]['options'])
                        choice_specify = input("Enter your choice (1-{}): ".format(len(menu[menu_id]['options'][choice]['options'])))
                        try:
                            choice_specify = int(choice_specify)
                        except:
                            print("Invalid choice. Press Enter to continue.")
                            wait_enter()
                            continue
                        if choice_specify > len(menu[menu_id]['options'][choice]['options']):
                            print("Invalid choice. Press Enter to continue.")
                            wait_enter()
                            continue         
                        if [menu[menu_id]['title'], choice] == ['Exams', 3] or [menu[menu_id]['title'], choice] == ['Exams', 4]: # Select exams by course or building
                            clear_screen()
                            menu[menu_id]['options'][choice]['options'][int(choice_specify)]['function'](database, int(choice_specify))
                            continue
                        elif [menu[menu_id]['title'], choice] == ['Rooms', 1]: # See Rooms with _accessory_
                            clear_screen()
                            menu[menu_id]['options'][choice]['options'][int(choice_specify)]['function'](database)
                            continue
                        else:
                            user_input = input(f"{menu[menu_id]['options'][choice]['options'][int(choice_specify)]['title']}: ")
                            clear_screen()
                            menu[menu_id]['options'][choice]['options'][int(choice_specify)]['function'](database, user_input)
            elif isinstance(menu[menu_id]['options'][choice], str):
                return
            break
        else:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()

def display_main_menu():
    clear_screen()
    print("Main Menu")
    for option, info in MENU.items():
        print(f"{option}: {info['title']}")

def main():
    while True:
        display_main_menu()
        choice = input("Enter your choice (1-{}): ".format(len(MENU)))

        if choice == str(len(MENU)):
            break
        
        try:
            choice = int(choice)
        except:
            print("Invalid choice. Press Enter to continue.")
            wait_enter()
            continue

        if choice in MENU:
            handle_menu(MENU, choice)
        else:
            print("Invalid choice. Press Enter to continue")
            wait_enter()
            continue

if __name__ == '__main__':
    main()