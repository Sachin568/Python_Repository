# importing the modules required
from collections import defaultdict
from prettytable import PrettyTable
import os
import sqlite3

# defining the function and reading the file and raising the exceptions
def file_reader(path, num_fields, expect, sep='\t'):
    try:
        fp = open(path, "r", encoding="utf-8")
    except FileNotFoundError:
        print(" can't open:", path)
    else:
        with fp:
            for n, line in enumerate(fp, 1):
                fields = line.rstrip('\n').split(sep)
                if len(fields) == fields:
                    print("field not present")
                elif n == 1 and expect:
                    continue
                else:
                    yield (fields)


# creating the respository to include the information of student and instructor in the dictionary
class Repository:
    # defining the function to get information of student and instructor from file to include in dictionary
    def __init__(self, path):
        self.path = path
        self.students = dict()
        self.instructors = dict()
        self.majors = dict()
 
        self.get_students(os.path.join(self.path, 'students.txt'))
        self.get_instructors(os.path.join(self.path, 'instructors.txt'))
        self.get_grades(os.path.join(self.path, 'grades.txt'))
        self.get_majors(os.path.join(self.path, 'majors.txt'))

    # defining the function to read the data of student
    def get_students(self, path):
        for cwid, name, course in file_reader(path, 3, 'CWID\tName\tMajor', sep='\t'):
            self.students[cwid] = Student(cwid, name, course)

    # defining the function to read the data of instructor
    def get_instructors(self, path):
        for cwid, name, department in file_reader(path, 3, 'CWID\tInstructor\tDept', sep='\t'):
            self.instructors[cwid] = Instructor(cwid, name, department)

    # reading the student information
    def get_grades(self, path):
        """Read Students data"""
        for student_cwid, course, grade, instructor_cwid in file_reader(path, 4, 'StudentCWID\tCourse\tGrade\tInstructorCWID', sep='\t'):
            if student_cwid in self.students:
                self.students[student_cwid].add_course(course, grade)
            else:
                print("Unknown student grade")

            if instructor_cwid in self.instructors:
                self.instructors[instructor_cwid].add_student(course)
            else:
                print("Unknown intructor grade")

    def get_majors(self, path):  # to get majors
        try:
            for dept, flag, course in file_reader(path, 3, 'major\tflag\tcours', sep='\t'):
                if dept in self.majors:
                    self.majors[dept].add_course(flag, course)
                else:
                    self.majors[dept] = Major(dept)
                    self.majors[dept].add_course(flag, course)
        except ValueError as err:
            print(err)

    def courses_remaining(self, student): # calculating the remaining course list
        required = self.majors[student.major].required_courses
        elective = self.majors[student.major].electives_courses
        passing_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        passed_courses = set()

        for course, grade in student.courses.items():
            if grade not in passing_grades:
                elective_remaining = None
            else:
                elective_remaining = elective
        return (passed_courses, required.difference(passed_courses), elective_remaining)

    # summary fo the student information allocated using prettytable
    def student_table(self):
        pt = PrettyTable(field_names=['CWID', 'Name', 'Completed Courses','Remaining Required','Remaining Electives'])      
        for student in self.students.values():
            pt.add_row(student.pt_row())
        print(pt)


    def join_data(self):
        for cwid in self.students:
            for grade in self.grades[cwid]:
                if grade.is_complete():
                    self.students[cwid].add_course(grade.course, grade.letter_grade)

        for cwid in self.instructors:
            for grade in self.grades[cwid]:
                if grade.is_teaching(cwid):
                    self.instructors[cwid].add_course(grade.course, grade.stud_cwid)

        for student in self.students.values():
            student.required_remain = self.majors[student.major].required - set(student.grade_check.keys())
            student.electives_remain = self.majors[student.major].electives - set(student.grade_check.keys())


    # summary of the instructor information allocated using prettytable
    def instructor_table(self):
        """A function that creates a table with instructor's information that is extracted from External Database."""
        DB_FILE = "C:\sqlite\810_startup.db"
        db = sqlite3.connect(DB_FILE)
        pt = PrettyTable(field_names = ['CWID', 'Name', 'Dept', 'Course', 'Student'])
        query = "select CWID, Name, Dept, Course, count(Course) as Students from (select * from instructor left join grade on CWID = CWID) group by Course order by CWID DESC "
        for row in db.execute(query):
                pt.add_row(row) 
        print (pt)
        db.close()


    def major_table(self):  # prettytable for major
        pt = PrettyTable(field_names=['Major', 'Required', 'Electives'])
        for major in self.majors.values():
            pt.add_row(major.pt_row())
        print(pt)


# creating the class to store the details of the student and student grade 
class Student:
    def __init__(self, cwid, name, major):
        self.courses = dict()
        self.cwid = cwid
        self.name = name
        self.major = major
        self.grade_check = list()
        self.courses_remaining = list()

    # adding the dictionary of course keys
    def add_course(self, course, grade):
        self.courses[course] = grade

    def pt_row(self):
        return [self.cwid, self.name, sorted(self.courses.keys()), sorted(self.grade_check), sorted (self.courses_remaining)]


# initializing the class to store the instructor details
class Instructor:
    def __init__(self, cwid, name, dept):
        self.courses = defaultdict(int)
        self.cwid = cwid
        self.name = name
        self.dept = dept

    # adding the student course to count
    def add_student(self, course):
        self.courses[course] += 1

    def pt_row(self):
        for course, count in self.courses.items():
            yield [self.cwid, self.name, self.dept, course, count]


class Major:
    """ creating major class """

    def __init__(self, dept, passing=None):
        self.dept = dept
        self.required = set()
        self.electives = set()

    def add_course(self, flag, course):

        if flag == 'R':  # creating flag 'R' for required courses
            self.required.add(course)
        elif flag == 'E':  # creating flag 'E' for elective courses
            self.electives.add(course)
        else:
            raise ValueError(f"Unexcepted flag {flag}")

    def grade_check(self, courses):
        remaining_required = self.required
        remaining_electives = self.electives
        grade_check = set()

        for course, grade in courses.items():
            if grade in ('A','A-','B+','B-','B','C+','C'):
                grade_check.add(course)

        remaining_required = self.required - grade_check

        if self._electives.intersection(grade_check):
            remaining_electives = None

        return (grade_check, remaining_required, remaining_electives)
  

    def pt_row(self):
        return [self.dept, self.required, self.electives]


def main():
    stevens_dir = "/Users/MSI/Desktop/Excercise/"
    repo = Repository(stevens_dir)
    print(" Student Summary ")
    repo.student_table()

    print(" Instructor Summary ")
    repo.instructor_table()

    print(" Majors Summary ")
    repo.major_table()


if __name__ == '__main__':
    main()
