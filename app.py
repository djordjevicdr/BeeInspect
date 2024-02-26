import os
import sqlite3
from flask import Flask, render_template, request
from datetime import date
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/inspect_all")
def inspect_all():
    db = os.path.join(app.root_path, 'pcelinjak.db')
    con = sqlite3.connect(db)    
    cur = con.cursor()  
    
    sql="""
    SELECT date, hive_id, interv, state, frames, note
    FROM inspect   
    ORDER BY date DESC
    """
    cur.execute(sql)
    rew=cur.fetchall()    
    con.close()    
    return render_template("inspect_all.html", review=rew)

@app.route("/inspect_last")
def inspect_last():
    db = os.path.join(app.root_path, 'pcelinjak.db')
    con = sqlite3.connect(db)    
    cur = con.cursor()  
    
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
    cur.execute(sql)
    rew=cur.fetchall()    
    con.close()    
    return render_template("inspect_last.html", review=rew)

@app.route("/inspect_by_id")
def inspect_by_id():
    db = os.path.join(app.root_path, 'pcelinjak.db')
    con = sqlite3.connect(db)    
    cur = con.cursor()

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
        cur.execute(sql, (hive_id,))
        rew=cur.fetchall()    
        con.close()        
        return render_template("inspect_by_id.html", hive_id=hive_id, review=rew)

@app.route("/shema")
def shema():

    shema = [
    [
        ["51", 0], ["52", 1], ["53", 1], ["54", 0], ["  ", 0], ["55", 0], ["56", 0], ["57", 0], ["  ", 0], ["58", 1], ["59", 1], ["5A", 1]
    ], 
    [
        ["41", 1], ["42", 1], ["43", 1], ["44", 0], ["  ", 0], ["45", 1], ["46", 1], ["47", 1], ["  ", 0], ["48", 1], ["49", 1], ["4A", 1]
    ],
    [
        ["31", 1], ["32", 1], ["33", 1], ["34", 0], ["  ", 0], ["35", 1], ["36", 0], ["37", 0], ["  ", 0], ["38", 1], ["39", 0], ["3A", 1]
    ],
    [
        ["21", 1], ["22", 1], ["23", 1], ["24", 0], ["  ", 0], ["25", 0], ["26", 0], ["27", 1], ["  ", 0], ["28", 0], ["29", 1], ["2A", 1]
    ],
    [
        ["11", 1], ["12", 1], ["13", 1], ["14", 1], ["  ", 0], ["15", 1], ["16", 1], ["17", 1], ["  ", 0], ["18", 0], ["19", 0], ["1A", 0]
    ],
    ]


    db = os.path.join(app.root_path, 'pcelinjak.db')
    con = sqlite3.connect(db)    
    cur = con.cursor()

    hive_id = request.args.get("hive_id")     

    if hive_id == None:
        return render_template("shema.html", hive_id=None, review=None, shema=shema)
    else:
        sql="""
        SELECT date, hive_id, interv, state, frames, note
        FROM inspect   
        WHERE hive_id=?
        ORDER BY date DESC, id DESC
        """
        cur.execute(sql, (hive_id,))
        rew=cur.fetchall()    
        con.close()        
        return render_template("shema.html", hive_id=hive_id, review=rew, shema=shema)
    
@app.route("/inspect_by_date")
def inspect_by_date():
    db = os.path.join(app.root_path, 'pcelinjak.db')
    con = sqlite3.connect(db)    
    cur = con.cursor()

    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    if (date_from == None) or (date_to == None):
        now = date.today()            
        date_from = str(now.year) + "-" + str(now.month).rjust(2, '0') + "-01" 
        date_to = now
        return render_template("inspect_by_date.html", date_from=date_from, date_to=date_to, review=None)
    else:
        sql="""
        SELECT date, hive_id, interv, state, frames, note
        FROM inspect   
        WHERE date BETWEEN ? and ?
        ORDER BY date DESC
        """
        cur.execute(sql, (date_from, date_to))
        rew=cur.fetchall()    
        con.close()        
        return render_template("inspect_by_date.html", date_from=date_from, date_to=date_to, review=rew)

@app.route("/inspect_add", methods=["GET", "POST"])
def inspect_add():  
    if request.method == "GET" :
        return render_template("inspect_add.html")
    else:
        try:
            db = os.path.join(app.root_path, 'pcelinjak.db')
            con = sqlite3.connect(db)
            cur = con.cursor()

            sql="""
            INSERT INTO inspect (date, hive_id, interv, state, frames, note)
            VALUES(?,?,?,?,?,?)
            """            
            date = request.form['date']
            hive_id = request.form['hive_id']            
            interv = request.form['interv']
            state = request.form['state']
            frames = request.form['frames']
            note = request.form['note']        

            cur.execute(sql, (date, hive_id, interv, state, frames, note))
            con.commit()
            _msg="Успешан упис"
            return render_template("inspect_add.html", msg=_msg)     
        except Exception as e:
            _msg = 'Грешка: {}'.format(str(e))
            return render_template("inspect_add.html", msg=_msg)
        
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")