DROP SCHEMA IF EXISTS grades CASCADE;

CREATE SCHEMA IF NOT EXISTS grades;

SET search_path TO grades;

CREATE TABLE student (
    email VARCHAR(128) PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    date_of_birth DATE,
    gpa FLOAT,
    state VARCHAR(64)
);

CREATE TABLE course (
    course_name VARCHAR(264) PRIMARY KEY
);

CREATE TABLE grades.is_enrolled (
    email VARCHAR(128) REFERENCES student(email) ON DELETE CASCADE,
    course_name VARCHAR(264) REFERENCES course(course_name) ON DELETE CASCADE,
    PRIMARY KEY(email, course_name)
);

CREATE TABLE building (
    building_name VARCHAR(128) PRIMARY KEY
);

CREATE TABLE room (
    room_name VARCHAR(32) PRIMARY KEY,
    capacity INTEGER,
    has_projector BOOLEAN DEFAULT 'f',
    has_computers BOOLEAN DEFAULT 'f',
	is_accessible BOOLEAN DEFAULT 'f',
    building_name VARCHAR(128) NOT NULL REFERENCES building(building_name) ON DELETE CASCADE
);

CREATE TABLE type (
    exam_name VARCHAR(64) PRIMARY KEY
);

CREATE TABLE exam (
    exam_id SERIAL PRIMARY KEY,
    exam_date DATE NOT NULL,
    course_name VARCHAR(264) NOT NULL REFERENCES course(course_name) ON DELETE CASCADE,
    exam_name VARCHAR(128) NOT NULL REFERENCES type(exam_name) ON DELETE CASCADE
);

CREATE TABLE examattempt (
	exam_id INTEGER REFERENCES exam(exam_id) ON DELETE CASCADE,
	room_name VARCHAR(32) NOT NULL REFERENCES room(room_name) ON DELETE CASCADE,
	email VARCHAR(128) REFERENCES student(email) ON DELETE CASCADE,
    grade FLOAT,
	PRIMARY KEY(exam_id, email)
);