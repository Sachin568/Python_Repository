from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/instructors')
def instructor_data():
    dbpath = "/sqlite/810_startup.db"
    try:
        db = sqlite3.connect(dbpath)
    except sqlite3.OperationalError:
        return f"Error: Unable to open database at {dbpath}"
    else:
        query = "SELECT CWID, Name, Dept, Course, COUNT(*) AS student FROM (SELECT * FROM instructor left JOIN grade on CWID = grade.InstructorCWID) GROUP BY Course ORDER BY CWID;"

        data = [{'cwid': cwid, 'name': name, 'dept': dept, 'course': course, 'students': students}
                for cwid, name, dept, course, students in db.execute(query)]

        db.close()

        return render_template("instructors.html",
                               title='Stevens Repository',
                               table_title='Instructors Table',
                               instructor=data)


app.run(debug=True)
