import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import datetime

df = pd.read_csv("../data/grades.csv")
df['student_name'] = df['first_name'].str.cat(df['last_name'], sep=' ')

def students_per_exam_per_room_plot(_):
    room_counts = df.groupby(['exam_name', 'room_name'])['email'].count().unstack(fill_value=0)

    room_counts.plot(kind='bar', stacked=True, figsize=(10, 10))
    plt.title("Number of Students per Exam Type")
    plt.xlabel("Exam Type")
    plt.ylabel("Number of Students")
    plt.xticks(rotation=45)
    plt.legend(title="Rooms", title_fontsize='12', loc='upper right')
    plt.tight_layout()
    plt.show()

def number_of_rooms_per_building_plot(_):
    room_counts = df.groupby('building_name')['room_name'].nunique()
    
    room_counts.plot(kind='bar', figsize=(10, 10), color='plum')
    plt.title("Number of Rooms per Building")
    plt.xlabel("Building")
    plt.ylabel("Number of Rooms")
    plt.xticks(rotation=45)
    plt.yticks([0, 1, 2, 3])
    plt.tight_layout()
    plt.show()

def number_of_courses_per_building_plot(_):
    course_count = df.groupby('building_name')['course_name'].nunique()

    course_count.plot(kind='pie', figsize=(6, 6), colors=['lightsalmon', 'yellowgreen', 'aqua', 'orchid', 'mediumpurple'], autopct='%1.1f%%')
    plt.title("Number of Courses per Building")
    plt.title("Number of Courses per Building")
    plt.ylabel('')
    plt.show()

def number_of_students_in_exam_per_date_plot(_):
    df['exam_date'] = pd.to_datetime(df['exam_date'])
    exam_date_counts = df.groupby(['exam_date', 'exam_name'])['student_name'].count().unstack(fill_value=0)

    exam_date_counts.plot(kind='line', marker='o', figsize=(15, 10))

    plt.title("Number of Students Doing an Examination per Date")
    plt.xlabel("Date")
    plt.ylabel("Number of Students")
    plt.grid(True)

    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))

    plt.show()

def gpa_distribuition_plot(_):
    gpa = df.groupby('student_name')['gpa'].mean()
    sns.displot(gpa, kde=True)
    mean_gpa = gpa.mean()
    median_gpa = gpa.median()
    std_dev = gpa.std()
    legend_text = f"Mean: {mean_gpa:.2f}, Median: {median_gpa:.2f}, Std Dev: {std_dev:.2f}"
    plt.legend([legend_text], loc='upper right')
    plt.show()




def exam_grade_distribution_per_course(_):
    plt.figure(figsize=(10, 6))  
    sns.boxplot(x='course_name', y='grade', data=df, hue='course_name', palette='Set3', legend=False)
    plt.title('Exam Grade Distributions by Course', fontsize=14)
    plt.xlabel('Course Name', fontsize=12)  
    plt.ylabel('Grade', fontsize=12)  
    plt.xticks(rotation=45, ha='right')  
    plt.tight_layout()  
    plt.show()


def number_of_students_per_state(_):
    state_counts = df['state'].value_counts().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    colors = plt.cm.Set3(np.linspace(0, 1, len(state_counts)))
    bars = plt.barh(state_counts.index, state_counts, color=colors, edgecolor='gray')

    plt.xlabel('Number of Students', fontsize=12)
    plt.ylabel('State', fontsize=12)
    plt.title('Student Counts by State', fontsize=16)
    plt.grid(axis='x', linestyle='--', alpha=0.6)  # Add a horizontal grid for reference

    for bar in bars:
        width = bar.get_width()
        plt.text(width+1, bar.get_y() + bar.get_height() / 2, int(width), ha='center', va='center', fontsize=8)

    plt.tight_layout()
    plt.show()


def age_distribution_best_students_by_course(_):
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    current_date = datetime.datetime.now()
    df['age'] = (current_date - df['date_of_birth']).apply(lambda x: x.days // 365)  # Calculate age in years
    best_students = df[df['grade'] >= 90]

    pivot_table = best_students.pivot_table(index='course_name', columns='age', values='grade', aggfunc='count', fill_value=0)

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table, cmap='YlGnBu', annot=True, fmt='d', cbar_kws={'label': 'Count'})
    plt.xlabel('Age', fontsize=12)
    plt.ylabel('Course', fontsize=12)
    plt.title('Age Distribution of Best Students (grade>=90) by Course', fontsize=16)
    plt.tight_layout()
    plt.show()
