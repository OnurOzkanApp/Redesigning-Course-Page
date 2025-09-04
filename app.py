# imports
import sqlite3  # sqlite3 library for accessing our database
from flask import Flask, render_template, request, g, session, redirect, url_for, escape, flash

DATABASE = './coursepage.db'  # declaring and assigning our database

# method connects to database
def get_db():
    db = getattr(g, '_database', None)  # gets current database, if exists
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)    # connects to new database otherwise
    return db

# converts tuples from database to dictionaries for use
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# returns resulting query request(
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

app = Flask(__name__)   #app being run
app.secret_key=b'secretforgithub'

# closes database when app terminates
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# General routing to catch non-defined links
@app.route('/<path>')
def nologin(path):
    if 'username' in session:
        username = session['username']
        return redirect(url_for(path))
    return redirect(url_for('login'))

# Default page
@app.route('/', methods=['GET'])
def index():
    #checks if user is signed in
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username = session['username'])
    #redirects to login otherwise
    return redirect(url_for('login'))

# Page for lecture content
# Logic follows default page
@app.route('/lectures', methods=['GET'])
def lectures():
    if 'username' in session:
        username = session['username']
        return render_template('lectures.html', username = session['username'])
    return redirect(url_for('login'))

# Page for lab content
# Logic follows default page
@app.route('/labs', methods=['GET'])
def labs():
    if 'username' in session:
        username = session['username']
        return render_template('labs.html', username = session['username'])
    return redirect(url_for('login'))

# Page for assignment content
# Logic follows default page
@app.route('/assignments', methods=['GET'])
def assignments():
    if 'username' in session:
        username = session['username']
        return render_template('assignments.html',  username = session['username'])
    return redirect(url_for('login'))

# Page for link content
# Logic follows default page
@app.route('/links', methods=['GET'])
def links():
    if 'username' in session:
        username = session['username']
        return render_template('links.html', username = session['username'])
    return redirect(url_for('login'))

# Page for student feedback content
@app.route('/feedback', methods=['GET','POST'])
def feedback():
    # When user submits feedback
    if request.method == 'POST':
        # Grabs feedback content
        instructor = request.form['instructors']
        feedback1 = request.form['student_feedback1']
        feedback2 = request.form['student_feedback2']
        feedback3 = request.form['student_feedback3']
        feedback4 = request.form['student_feedback4']

        # Query to search for instructor
        instructor_query = query_db("SELECT instructorid,username FROM Accounts NATURAL JOIN Instructors", args=(), one=False)
        for item in instructor_query:
            if item[1] == instructor:
                instructorid = item[0]

        # Query to define a feedback id for the new feedback
        max_feedbackid = 0
        feedbackid_query = query_db("SELECT feedbackid FROM Feedback", args=(), one=False)
        for item in feedbackid_query:
            max_feedbackid = max(max_feedbackid, item[0])
        feedbackid = max_feedbackid+1

        # Logic for inserting data into database taken from
        # https://pythonbasics.org/flask-sqlite/
        cur = get_db()
        cur.execute(
                """INSERT INTO Feedback 
                (feedbackid,instructorid,response1,response2,response3,response4)
                VALUES (?,?,?,?,?,?)
                """,(feedbackid,instructorid,feedback1,feedback2,feedback3,feedback4))
        cur.commit()
    # GET request for the webpage, ie no form submission
    # Logic follows default page
    if 'username' in session and session['usertype'] == 'student':
        username = session['username']

        # Queries for instructors in DB, for instructor specific feedback
        instructor_query = query_db("SELECT username FROM Accounts WHERE usertype='instructor'", args=(), one=False)

        return render_template('studentfeedback.html', username = session['username'],instructors = instructor_query)
    elif 'username' in session and session['usertype'] == 'instructor':
        # For when instructors visit this page

        # Queries for existing instructor accounts
        sql = """ 
            SELECT feedbackid, response1, response2, response3, response4, username
            FROM Feedback F, Instructors I, Accounts A
            WHERE (F.instructorid = I.instructorid) AND (I.userid = A.userid) AND A.username = ?
            """
        # Grabs instructor id to show them their own feedback only
        results = query_db(sql, [session['username']], one=False)
        return render_template('instructorfeedback.html', username = session['username'], feedbacks = results)
    return redirect(url_for('login'))

# Page for student assignment grades
@app.route('/grades', methods=['GET','POST'])
def grades():
    
    # Form entry from user (instructor grade changes)
    if request.method == 'POST':
        #Grabs data from user entry
        assessment_name = request.form['select_assessment']
        student_name = request.form['select_student']
        grade = request.form['grade']

        # SQL queries for getting data from DB
        sql_assessmentid = """
                        SELECT assessmentid FROM Assessments
                        WHERE assessmentname = ?
                        """

        sql_students = """
                    SELECT studentid FROM
                    Students s, Accounts a
                    WHERE s.userid = a.userid AND a.username = ?
                    """

        sql_grades = """
                    SELECT * FROM Grades
                    """
        
        # Queries for assessmentid, student id and grades for adding into DB
        results_assessmentid = query_db(sql_assessmentid, [assessment_name], one=True)
        results_students = query_db(sql_students, [student_name], one=True)
        results_grades = query_db(sql_grades, args=(), one=False)

        # Checks given form data with existing grades data in DB
        for item in results_grades:
            # If grade already exists, update the grade
            if item[0] == results_assessmentid[0] and item[1] == results_students[0]:
                # Logic from flask/sqlite documentation
                sql_change = """
                            UPDATE Grades
                            SET grade = ?
                            WHERE assessmentid = ? and studentid = ?
                            """
                cur = get_db()
                cur.execute(sql_change, (grade,results_assessmentid[0],results_students[0]))
                cur.commit()
                return redirect(url_for('grades'))
            else:
                # Otherwise, add a new grade
                sql_change = """
                            INSERT INTO Grades (assessmentid, studentid, grade)
                            VALUES(?,?,?)
                            """
        # As said before, logic from flask/sqlite documentation
        cur = get_db()
        cur.execute(sql_change, (results_assessmentid[0],results_students[0],grade))
        cur.commit()
        return redirect(url_for('grades'))

    # Logic follows from default page regarding user access
    if 'username' in session and session['usertype'] == 'student':
        return redirect(url_for('studentgradesassignments'))
    elif 'username' in session and session['usertype'] == 'instructor':
        # Variables for page content from DB
        assessments=["assignment","lab","midterm","final"]

        results_grades = []
        results_assessments = []
        results_students = []

        assignments = []
        labs = []
        midterms = []
        finals = []

        results_assessments.append(assignments)
        results_assessments.append(labs)
        results_assessments.append(midterms)
        results_assessments.append(finals)

        # Performs queries for each type of assessment to grab their data
        for item in assessments:
            sql_grades = """ 
                            SELECT assessmentname,username,studentid,grade
                            FROM (SELECT * FROM Accounts
                            NATURAL JOIN Students)
                            NATURAL JOIN
                            (SELECT * FROM Grades
                            NATURAL JOIN Assessments WHERE assessmenttype=?)
                            ORDER BY assessmentname ASC
                            """
            results_grades.append(query_db(sql_grades, [item], one=False))

        # Queries for getting assessment names for each type of assessment
        for item in results_assessments:
            sql_assessments = """
                            SELECT assessmentname
                            FROM Assessments WHERE assessmenttype=?
                            """
            temp = query_db(sql_assessments, [assessments[results_assessments.index(item)]], one=False)
            
            # Assigns assessment names to a list of lists.
            # One big list (results_assessments) contains 4 lists, one for each type of assessment,
            # of which, these lists contains the the names for each assessment
            # of that type.
            for name in temp:
                item.append(name)

        # Queries to get the usernames of the students
        sql_students = """
                        SELECT username FROM Accounts WHERE usertype='student'
                        """
        results_students = query_db(sql_students, args=(), one=False)

        return render_template('instructorgrades.html', username = session['username'], results_grades=results_grades, results_assessments=results_assessments, results_students=results_students, assessments=assessments)
    return redirect(url_for('login'))

# Helper function for adding remark requests
# Returns true or false, depending on whether request was added successfully
def processRemarks(assessment_name, reason, username) -> bool:
    # SQL queries for getting current remarks, assessments, students
    sql_remarks = """
                    SELECT assessmentid,studentid,status,remarkid FROM Remarks
                    """

    sql_assessments = """
                    SELECT assessmentid FROM Assessments WHERE assessmentname=?
                    """

    sql_student = """
                SELECT studentid FROM
                (SELECT * FROM Accounts NATURAL JOIN Students)
                WHERE username=?
                """

    # Queries for data from DB
    results_remarks = query_db(sql_remarks, args=(), one=False)
    results_assessments = query_db(sql_assessments, [assessment_name], one=True)
    results_students = query_db(sql_student, [username],one=True)

    # Assigns values to assessmentid and studentid from SQL queries
    assessmentid = results_assessments[0]
    studentid = results_students[0]

    # Checks queried data for remakrs, and compares request with open requests
    for item in results_remarks:
        # Case for existing remark request of the same assessment and student
        # that is already open
        if item[0] == assessmentid and item[1] == studentid and item[2] == 'open':
            return False

    # Assigns new remark ID for this request
    max_remark = 0
    for item in results_remarks:
        max_remark = max(max_remark, item[3])
    remarkid = max_remark+1

    # Inserts new remark into DB
    cur = get_db()
    cur.execute(
        """INSERT INTO Remarks 
        (remarkid, assessmentid,studentid,reason,status)
        VALUES (?,?,?,?,?)
        """,(remarkid,assessmentid,studentid,reason,'open'))
    cur.commit()
    return True

# Helper function for querying a student's grades and other info
# for an assessment type (includes remark status of a given grade if exists)
# returns a list of results containing rows of query
def getGrades(assessmenttype,username):
    # Queries for getting a student's marks 
    sql_student = """
                SELECT studentid FROM Students NATURAL JOIN
                (SELECT userid FROM Accounts WHERE username=?)
                """
    sql_assessments = """
                    SELECT assessmentname, grade, assessmentid FROM
                    (SELECT grade, assessmentid FROM Grades WHERE studentid=?)
                    NATURAL JOIN
                    (SELECT * FROM Assessments  WHERE assessmenttype = ?)
                    ORDER BY assessmentname ASC
                    """

    # Queries for a student's student id
    results_student = query_db(sql_student,[username], one=True)

    studentid = results_student[0]  # Assigns student id to a variable

    # Queries for a student's grades for a particular assessment type
    results_assessments = query_db(sql_assessments,[studentid,assessmenttype], one=False)

    # Checks and adds remark status for a student's grades
    for item in results_assessments:
        remark_status = ""
        # Queries for status of remark for a given grade
        sql_remark = """
                    SELECT status FROM Remarks
                    WHERE remarkid = 
                    (SELECT MAX(remarkid) FROM Remarks 
                    WHERE studentid=? AND assessmentid=?)
                    """
        temp = query_db(sql_remark,[studentid,item[2]], one=True)
        # If a status for such grade exists, add its status to be returned (o/w add empty string)
        if temp != None:
            remark_status = "Remark status: " + temp[0]
        results_assessments[results_assessments.index(item)]+=(remark_status,)
    return results_assessments

# Page for student assignment grades
@app.route('/grades/assignments', methods=['GET','POST'])
def studentgradesassignments():
    # Receives form data        
    if request.method=='POST':
        # Grabs submitted data
        assessment_name = request.form['select_remark']
        reason = request.form['remark_request']
        username = session['username']

        # If request is not added to DB, send student a message
        if (not processRemarks(assessment_name,reason,username)):
            flash("A pending request already exists")
        else:
            flash("Request submitted")
        
    
    # User access logic follows default page
    if 'username' in session and session['usertype'] == 'student':
        username = session['username']

        #Queries for a particular student's grades
        results = getGrades('assignment',username)
        
        # Renders the page with their marks
        return render_template('grades_assignments.html', username = username, assessments = results)
    return redirect(url_for('grades'))

# Page for studentlabs grades
# Logic /grades/assignments
@app.route('/grades/labs', methods=['GET','POST'])
def studentgradeslabs():
    if request.method=='POST':
        assessment_name = request.form['select_remark']
        reason = request.form['remark_request']
        username = session['username']

        if (not processRemarks(assessment_name,reason,username)):
            flash("A pending request already exists")
        else:
            flash("Request submitted")

    if 'username' in session and session['usertype'] == 'student':
        username = session['username']

        #Queries for a particular student's grades
        results = getGrades('lab',username)

        return render_template('grades_labs.html', username = username, assessments = results)
    return redirect(url_for('grades'))

# Page for student midterm grade
# Logic follows /grades/assignments
@app.route('/grades/midterm', methods=['GET', 'POST'])
def studentgradesmidterm():
    if request.method=='POST':
        assessment_name = request.form['select_remark']
        reason = request.form['remark_request']
        username = session['username']

        if (not processRemarks(assessment_name,reason,username)):
            flash("A pending request already exists")
        else:
            flash("Request submitted")

    if 'username' in session and session['usertype'] == 'student':
        username = session['username']

        #Queries for a particular student's grades
        results = getGrades('midterm',username)

        return render_template('grades_midterm.html', username = username, assessments = results)
    return redirect(url_for('grades'))

# Page for studentfinal grade
# Logic follows /grades/assignments
@app.route('/grades/final', methods=['GET', 'POST'])
def studentgradesfinal():
    if request.method=='POST':
        assessment_name = request.form['select_remark']
        reason = request.form['remark_request']
        username = session['username']

        if (not processRemarks(assessment_name,reason,username)):
            flash("A pending request already exists")
        else:
            flash("Request submitted")

    if 'username' in session and session['usertype'] == 'student':
        username = session['username']
        
        #Queries for a particular student's grades
        results = getGrades('final',username)
        
        return render_template('grades_final.html', username = username, assessments = results)
    return redirect(url_for('grades'))

# Page for user login
# Logic taken from lecture demo
@app.route('/login', methods=['GET','POST'])
def login():
    #Takes user form submission
    if request.method == 'POST':
        #Queries for existing accounts
        sql = """ 
            SELECT *
            FROM Accounts 
            """
        results = query_db(sql, args=(), one=False)

        #Compares user input with existing accounts
        for result in results:
            # If pass/user is correct, assign session variables appropriately and user type
            if result[1] == request.form['username'] and result[2] == request.form['password']:
                session['username'] = request.form['username']
                session['usertype'] = result[3]
                return redirect(url_for('index'))
        # Otherwise, send them a message and refresh oage
        flash("Invalid username/password")
        return redirect(url_for('login'))

    #Redirects to home page if already signed in
    elif 'username' in session:
        return redirect(url_for('index'))
    #Otherwise, send user to login page
    else:
        return render_template('login.html',username='username',password='password')

# Logic for inserting data into database taken from
# https://pythonbasics.org/flask-sqlite/
@app.route('/signup', methods=['GET','POST'])
def signup():
    #Takes user form submission
    if request.method == 'POST':
        #Assigns user input to variables
        username = request.form['username']
        password = request.form['password']
        usertype = request.form['usertype'].lower()

        # Restriction on having whitespaces in username
        if " " in username:
            flash("You cannot have whitespaces in your username")
            return redirect(url_for('signup'))
        if len(password) < 1 or " " in password:
            flash("Your password contains whitespaces or is too short")
            return redirect(url_for('signup'))

        max_userid = 0 # Used for creating new userid

        #Queries for existing user name (also creates new user id)
        results = query_db("SELECT username, userid FROM Accounts", args=(), one=False)
        for result in results:
            max_userid = max(max_userid, result[1])
            if result[0] == username:
                # this is taken from flask documentation
                # https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
                flash("The user name: '" + username + "', is already in use", 'error')
                return redirect(url_for('signup'))
               
        # this line will only be reached if username does not
        # exist already, thus creating a new and unique userid
        userid = max_userid + 1        
            
        # ~~ Logic source from pythonbasics.org
        # Fetches current database and executes sql command to
        # insert new account into database
        cur = get_db()
        cur.execute(
            """INSERT INTO Accounts 
            (userid,username,password,usertype)
            VALUES (?,?,?,?)
            """,(userid,username,password,usertype))
        cur.commit()

        # inserts new entry into students/instructors table where applicable
        # for use of studentid or instructor id
        max_alt_id = 0

        # Defines SQL query for new user being added, into Student and Instructor
        # table (from DB) appropriately
        if usertype == 'student':
            results_alt = query_db("SELECT studentid FROM Students", args=(), one=False)
            alt_query = """
                        INSERT INTO Students
                        (studentid, userid)
                        VALUES (?,?)
                        """
        else:
            results_alt = query_db("SELECT instructorid FROM Instructors", args=(), one=False)
            alt_query = """
                        INSERT INTO Instructors
                        (instructorid, userid)
                        VALUES (?,?)
                        """
        # Creates new studentid/instructorid
        for result in results_alt:
            max_alt_id = max(max_alt_id, result[0])
        altid = max_alt_id + 1

        # Adds new instructor/student into Students/Instructors table
        cur = get_db()
        cur.execute(alt_query,(altid,userid))
        cur.commit()
        cur.close()

        #Once new account created, redirect to login
        flash("Account created")
        return redirect(url_for('login')) #add msg for acc created
    #Sends user to sign up page (with form)
    return render_template('signup.html',username='username',password='password',usertpe='usertype')

#User logout
#Logic taken from lecture demo
@app.route('/logout')
def logout():
    #Removes username and usertype from current session and redirects to login
    session.pop('username', None)
    session.pop('usertype', None)
    return redirect(url_for('login'))

# Page for instructor remarks
@app.route('/instructorremark', methods=['GET','POST'])
def insremark():
    # Form submission
    if request.method=='POST':
        # Gets and parses data from form request
        remark_data = (request.form['closebutton'][1:-1]).replace("'","").split(", ")
        assessment_name = remark_data[2]
        student_name = remark_data[0]

        # Defines queries for getting data from assessment, students, and remarks tables
        sql_assessments ="""
                        SELECT assessmentid FROM Assessments WHERE assessmentname = ?
                        """

        sql_students = """
                    SELECT studentid FROM Students s, Accounts a
                    WHERE s.userid = a.userid AND a.username = ?
                    """
        
        # For closing a remark request
        sql_remarks = """
                    UPDATE Remarks
                    SET status='closed'
                    WHERE assessmentid=? AND studentid=? AND status='open'
                    """
        
        # Queries for data
        results_assessments = query_db(sql_assessments, [assessment_name], one=True)
        results_students = query_db(sql_students, [student_name], one=True)

        # Executes changes to Remarks table (closing an open remark request)
        cur=get_db()
        cur.execute(sql_remarks,(results_assessments[0],results_students[0]))
        cur.commit()

    # User access follows default page
    if 'username' in session and session['usertype'] == 'instructor':
            # Query grabs remark requests that are open
            sql = """ 
                SELECT username, reason, assessmentname
                FROM Remarks Rem, Students S, Accounts A, Assessments A2
                WHERE (Rem.studentid = S.studentid) AND (S.userid = A.userid) AND
                (Rem.assessmentid=A2.assessmentid) AND Rem.status='open'
                """
            results = query_db(sql, args=(), one=False)
            return render_template('instructorremark.html', username = session['username'], remarks = results)
    # If user is not an instructor, send to grades
    return redirect(url_for('grades'))

if __name__ == '__main__':
    app.debug = True
    app.run()