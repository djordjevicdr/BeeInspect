import os
import sqlite3
from flask import Flask, render_template, request, session, g
from datetime import date
import re, hashlib

app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = '30f4e171b53b4e86bf0962e5cbb0dec2'

_USER_ID=''

# D A T A B A S E

DATABASE = 'beenote.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_apiaryes():
    conn = get_db()
    cursor = conn.cursor()    
    cursor.execute("SELECT id, name FROM apiary  WHERE user_id=?", [_USER_ID])
    apiaryes = cursor.fetchall()
    cursor.close()
    return apiaryes


# I N D E X

@app.route("/")
def index():
    #if not session['loggedin']:
    if not 'username' in session:
        request.cookies.clear
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)


# U S E R - L O G I N / R E G I S T E R        
        
@app.route("/login", methods=['GET', 'POST'])
def login():
    global _USER_ID 
    _msg = ''
    _succ = False
    #_user = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:        
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()

        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

        sql="""
        SELECT ID, email FROM user
        WHERE email = ? AND password = ?
        """
        cursor.execute(sql, (email, password))       
        account = cursor.fetchone()
        cursor.close()
        
        if account:            
            session['loggedin'] = True
            session['id'] = account[0]
            session['email'] = account[1]
            session['username'] = account[1].split("@")[0]
            #_user = session['email'] 
            _USER_ID = account[0]           
            _msg = 'Успешно сте улоговани'
            _succ = True                      
        else:            
            _msg = 'Нетачан eMail/лозинка!'    
    return render_template('login.html', msg=_msg, succ=_succ, timeout=1000)

@app.route('/register', methods=['GET', 'POST'])
def register():
    _msg = ''
    _succ = False
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']       
        password = request.form['password']       

        conn = get_db()
        cursor = conn.cursor()

        sql="""
        SELECT email FROM user
        WHERE email = ?
        """

        cursor.execute(sql, (email, ))
        account = cursor.fetchone()        
        
        if account:
            _msg = 'Налог већ постоји!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            _msg = 'Погрешна eMail адреса!'        
        else:            
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()            
            cursor.execute('INSERT INTO user VALUES (NULL, ?, ?, ?, ?)', (firstname, lastname, email, password))
            conn.commit()
            _msg = 'Успешно сте креирали нови налог! Сада се пријавите са параметрима креираног налога.'
            _succ = True
        cursor.close()      
    elif request.method == 'POST':        
        _msg = 'Молимо попуните формулар!'      
    return render_template('register.html', msg=_msg, succ=_succ, timeout=1200)

@app.route('/logout')
def logout():
    global _USER_ID
    session['loggedin'] = False    
    session.pop('username', None)
    _USER_ID=''
    return render_template("index.html")


# P C E L I N J A K - A P I A R Y

# Pcelinjak - Add

@app.route("/apiary_add", methods=["GET", "POST"])
def apiary_add():
    if not 'username' in session:
        return render_template("denied.html")
    
    if request.method == "GET" :
        return render_template("apiary_add.html")
    else:
        try:
            conn = get_db()
            cursor = conn.cursor()                    
            
            name = request.form['name']
            location = request.form['name']
            address = request.form['address']
            description = request.form['description']

            sql="""
            INSERT INTO apiary (user_id, name, location, address, description)
            VALUES(?,?,?,?,?)
            """

            cursor.execute(sql, (_USER_ID, name, location, address, description))
            conn.commit()
            cursor.close()
            _msg="Успешан упис"
            _succ=True
            return render_template("apiary_add.html", msg=_msg)     
        except Exception as e:
            cursor.close()
            _msg = 'Грешка: {}'.format(str(e))
            return render_template("apiary_add.html", msg=_msg, succ=_succ, timeout=1000)


# P R E G L E D I
        
# Pregledi - novi pregled

@app.route("/inspect_add", methods=["GET", "POST"])
def inspect_add():
    if not 'username' in session:
        return render_template("denied.html")
    conn = get_db()
    cursor = conn.cursor()
         
    _apiary = get_apiaryes()    

    if not _apiary:
        return render_template("denied.html")
     
    if request.method == "GET" :
        _date = date.today()
        return render_template("inspect_add.html", apiary=_apiary, date=_date)
    else:
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            _date = request.form['date']
            _apiary_id = request.form['apiary_id']
            _apiary_id = int(_apiary_id)
            _hive_id = request.form['hive_id']            
           
                        
            _interv = request.form['interv']
            _state = request.form['state']
            _frames = request.form['frames']
            _note = request.form['note']

            sql="""
            INSERT INTO inspect (user_id, apiary_id, hive_id, date, interv, state, frames, note)
            VALUES(?,?,?,?,?,?,?,?)
            """ 

            cursor.execute(sql, (_USER_ID, _apiary_id, _hive_id, _date, _interv, _state, _frames, _note))
            conn.commit()
            cursor.close()
            _msg="Успешан упис"
            return render_template("inspect_add.html", msg=_msg, apiary_id=_apiary_id, apiary=_apiary, date=_date)     
        except Exception as e:
            cursor.close()
            _msg = 'Грешка: {}'.format(str(e))
            return render_template("inspect_add.html", msg=_msg, apiary_id=_apiary_id, apiary=_apiary, date=_date)        
        
# Pregledi po datumu
    
@app.route("/inspect_by_date", methods=['GET', 'POST'])
def inspect_by_date():
    if not 'username' in session:
        return render_template("denied.html")
    
    conn = get_db()
    cursor = conn.cursor()
         
    _apiary = get_apiaryes()    

    if not _apiary:
        return render_template("denied.html")
    
    emptyvalues = ["", "''", " ", "' '", None, '""', '" "']
    
    _apiary_id = request.args.get("apiary_id")
    if _apiary_id not in emptyvalues:
        _apiary_id = int(_apiary_id)
    _hive_id = request.args.get("hive_id")
    _date_from = request.args.get("date_from")
    _date_to = request.args.get("date_to")    

    if _hive_id in emptyvalues:
        _hive_id_empty = True
    else:
        _hive_id_empty = False

    if (_date_from in emptyvalues) or (_date_to in emptyvalues) or (_apiary_id in emptyvalues):
        now = date.today()
        #_date_from = str(now.year) + "-" + str(now.month).rjust(2, '0') + "-01"
        _date_from = str(now.year) + "-01-01"  
        _date_to = now
        _hive_id = ''
        return render_template("inspect_date.html", date_from=_date_from, date_to=_date_to, apiary_id=_apiary_id, hive_id=_hive_id, apiary=_apiary, databee=None)   
            
    if _hive_id_empty:
        sql="""
        SELECT date, hive_id, interv, state, frames, note
        FROM inspect   
        WHERE (user_id=?) and (apiary_id=?) and (date BETWEEN ? and ?)
        ORDER BY date DESC, hive_id ASC
        """
        cursor.execute(sql, (_USER_ID, _apiary_id, _date_from, _date_to))
    else:
        sql="""
        SELECT date, hive_id, interv, state, frames, note
        FROM inspect   
        WHERE (user_id=?) and (apiary_id=?) and (hive_id=?) and (date BETWEEN ? and ?)
        ORDER BY date DESC
        """
        cursor.execute(sql, (_USER_ID, _apiary_id, _hive_id, _date_from, _date_to))

    _data=cursor.fetchall()    
    cursor.close()   
    if _hive_id_empty:      
        return render_template("inspect_date_all.html", date_from=_date_from, date_to=_date_to, apiary_id=_apiary_id, apiary=_apiary, databee=_data)
    else:
        return render_template("inspect_date_id.html", date_from=_date_from, date_to=_date_to, apiary_id=_apiary_id, hive_id=_hive_id, apiary=_apiary, databee=_data)  

# Pregled - poslednji
    
@app.route("/inspect_last")
def inspect_last():
    if not 'username' in session:
        return render_template("denied.html")
    
    conn = get_db()
    cursor = conn.cursor()  
    
    sql="""
    SELECT I.hive_id, I.date, I.interv, I.state, I.frames, I.note
    FROM inspect AS I
    JOIN
    (
    SELECT hive_id, MAX(date) ldate
    FROM inspect
    GROUP BY hive_id
    ) as M
    ON I.hive_id = M.hive_id AND I.date = M.ldate
    ORDER BY    I.hive_id
    """
    cursor.execute(sql)
    _data=cursor.fetchall()    
    cursor.close()    
    return render_template("inspect_last.html", databee=_data)
    
#Pregled - ID

@app.route("/inspect_by_id")
def inspect_by_id():
    if not 'username' in session:
        return render_template("denied.html")
    
    conn = get_db()
    cursor = conn.cursor()  

    hive_id = request.args.get("hive_id")     

    if hive_id == None:
        return render_template("inspect_by_id.html", hive_id=None, review=None)
    else:
        sql="""
        SELECT date, hive_id, interv, state, frames, note
        FROM inspect   
        WHERE hive_id=?
        ORDER BY date DESC
        """
        cursor.execute(sql, (hive_id,))
        _data=cursor.fetchall()    
        cursor.close()        
        return render_template("inspect_by_id.html", hive_id=hive_id, databee=_data)
    
#Pcelinjak shema

@app.route("/shema")
def shema():
    if not 'username' in session:
        return render_template("denied.html")

    _shema = [
    [
        ["51", 0], ["52", 1], ["53", 1], ["54", 0], ["  ", 0], ["55", 0], ["56", 0], ["57", 0], ["  ", 0], ["58", 1], ["59", 0], ["5A", 1]
    ], 
    [
        ["41", 1], ["42", 1], ["43", 1], ["44", 0], ["  ", 0], ["45", 0], ["46", 0], ["47", 1], ["  ", 0], ["48", 1], ["49", 0], ["4A", 0]
    ],
    [
        ["31", 1], ["32", 1], ["33", 0], ["34", 0], ["  ", 0], ["35", 1], ["36", 0], ["37", 0], ["  ", 0], ["38", 0], ["39", 0], ["3A", 0]
    ],
    [
        ["21", 0], ["22", 1], ["23", 1], ["24", 0], ["  ", 0], ["25", 0], ["26", 0], ["27", 0], ["  ", 0], ["28", 0], ["29", 1], ["2A", 1]
    ],
    [
        ["11", 1], ["12", 1], ["13", 1], ["14", 1], ["  ", 0], ["15", 1], ["16", 0], ["17", 1], ["  ", 0], ["18", 0], ["19", 0], ["1A", 0]
    ],
    ]


    conn = get_db()
    cursor = conn.cursor() 

    hive_id = request.args.get("hive_id")     

    if hive_id == None:
        return render_template("shema.html", hive_id=None, review=None, shema=_shema)
    else:
        sql="""
        SELECT date, hive_id, interv, state, frames, note
        FROM inspect   
        WHERE hive_id=?
        ORDER BY date DESC, id DESC
        """
        cursor.execute(sql, (hive_id,))
        _data=cursor.fetchall()    
        cursor.close()        
        return render_template("shema.html", hive_id=hive_id, databee=_data, shema=_shema)