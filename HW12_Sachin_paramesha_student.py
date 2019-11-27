from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route('/students')
def students_data():
    dbpath = "/sqlite/810_startup.db"
    try:
        db = sqlite3.connect(dbpath)
    except sqlite3.OperationalError:
        return f"Error: Unable to open database at {dbpath}"
    else:
        query = "SELECT s.cwid, s.name, s.major, count(g.Course) as Completed_Courses from student s join grade g on s.CWID = g.StudentCWID group by s.CWID, s.Name, s.Major"

        data = [{'cwid': cwid, 'name': name, 'major': major, 'complete': complete}
                for cwid, name, major, complete in db.execute(query)]

        db.close()

        return render_template("students.html",
                               title='Stevens Repository',
                               table_title='Students Table',
                               student=data)


app.run(debug=True)
