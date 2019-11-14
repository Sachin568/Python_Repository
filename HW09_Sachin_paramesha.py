# importing the modules required
from collections import defaultdict
from prettytable import PrettyTable

# defining the function and reading the file and raising the exceptions 
def file_reader(path, num_fields, expect, sep='\t'):
    try:
        fp = open(path, 'r')
    except FileNotFoundError:
        raise FileNotFoundError("Entered file is not found")
    else:
        with fp:
            for line_num, line in enumerate(fp):
                fields = line.strip().split(sep)
                if len(fields) != num_fields:
                    raise ValueError("Excepted number of col")
                else:
                    yield fields

# creating the respository to include the information of student and instructor in the dictionary
class Repository():
        # defining the function to get information of student and instructor from file to include in dictionary
        def __init__(self):
            self.students = defaultdict()
            self.instructors = defaultdict()

            self.get_students("students.txt")
            self.get_instructors("instructors.txt")
            self.get_grades("grades.txt")

        # defining the function to read the data of student
        def get_students(self,path):
            for cwid,name,course in file_reader(path,3,'cwid\tname\tmajor'):
                self.students[cwid] = Student(cwid,name,course)
                
        # defining the function to read the data of instructor
        def get_instructors(self, path):
            for cwid, name, department in file_reader(path, 3,'cwid\tname\tdept'):
                self.instructors[cwid] = Instructor(cwid, name, department)

        # reading the student information 
        def get_grades(self, path):
            """Read Students data"""
            for student_cwid,course,grade,instructor_cwid in file_reader(path, 4,'student_cwid\tcourse\tgrade\tinstructor_cwid'):
                if student_cwid in self.students:
                    self.students[student_cwid].add_course(course, grade)
                else:
                    print("Unknown student grade")

                if instructor_cwid in self.instructors:
                    self.instructors[instructor_cwid].add_student(course)
                else:
                    print("Unknown intructor grade")

        # summary fo the student information allocated using prettytable
        def student_table(self):
            pt = PrettyTable(field_names=['CWID','Name','Completed Courses'])
            for student in self.students.values():
                pt.add_row(student.pt_row())
            print(pt)

        # summary of the instructor information allocated using prettytable
        def instructor_table(self):
            pt = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Course', 'Student'])
            for instructor in self.instructors.values():
                for row in instructor.pt_row():
                    pt.add_row(row)
            print(pt)

# creating the class to store the details of the student and student grade 
class Student():
    def __init__(self, cwid, name, major):
        self.courses = defaultdict(str)
        self.cwid = cwid
        self.name = name
        self.major = major
    
    # adding the dictionary of course keys
    def add_course(self, course, grade):
        self.courses[course] = grade

    def pt_row(self):
        return [self.cwid, self.name, sorted(self.courses.keys())]

# initializing the class to store the instructor details
class Instructor():
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



def main():

    repo = Repository()
    print(" Student Summary ")
    repo.student_table()

    print(" Instructor Summary ")
    repo.instructor_table()

if __name__ == '__main__':
    main()



  
