from flask import Flask,render_template
import sqlite3
app = Flask(__name__)

@app.route("/")
def hello():
    return 'Hello World'

@app.route("/instructor_summary")
def instructor_summary():
    DB_FILE = r"810_startup.db"
            
    query="""select i.*, g.course,count(*) as students from instructors i join grades g on g.'Grade Instructor_CWID'=i.CWID 
    group by course order by i.Dept desc, i.name DESC"""
    db = sqlite3.connect(DB_FILE)
    rows = db.execute(query)    
    instructors = [{'cwid':cwid,'name':name,'department':department,'courses':courses,'students':students} for cwid,name,department,courses,students in rows]
    db.close() 
    return render_template('instructors_template.html',title='Stevens Repository',table_title='Number of Students by course and instructor',instructors=instructors)

app.run(debug=True)



