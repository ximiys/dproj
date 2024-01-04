from flask import *
import pymysql
import re
import bcrypt
import urllib.parse

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#подключение к базе данных
def connect():
    connection = pymysql.connect(
        host='141.8.192.151',
        port=3306,
        user='f0893674_librarum',
        password='librarum123',
        database='f0893674_librarum'
    )
    return connection

#главная страница с кнопками "войти" и "зарегестрироваться" 
@app.route("/")
def logup():
    if 'user_id' in session:
        return redirect('main')
    return render_template('logup.html')

#страница для входа в аккаунт
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        try:
            connection = connect()
            cursor=connection.cursor()
        except: 
            return redirect('login?dberr=true')
        email=request.form['email']
        sql=f"SELECT prof_id, password FROM User_Profile WHERE login='{email}'"
        cursor.execute(sql)
        try:
            result=cursor.fetchall()
            hashed=result[0][1]
            usrID=result[0][0]
            connection.close()
        except:
            return redirect('login?usrnotfound=true')
        password=request.form['password']
        if password==hashed:
            session['user_id']=usrID
            return redirect('main')
        return redirect('login?incorrpass=true')
    
    return render_template('login.html')

#страница для создания аккаунта
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        try:
            connection = connect()
            cursor=connection.cursor()
        except: 
            print(1)
            return redirect('signup?dberr=true')
        email=request.form['email']
        sql=f"SELECT count(*) from User_Profile WHERE login = '{email}'"
        cursor.execute(sql)
        res=cursor.fetchall()[0][0]
        if(res!=0):
            return redirect('signup?usrexists=true')
        password=request.form['password']
        if(len(password)<8 or re.search(r'\s', password)):
            return redirect('signup?passerr=true')
        username=request.form['username']
        sql=f"INSERT INTO User_Profile(login,password,app_lang_id,book_lang_id,Username) VALUES ('{email}','{password}',1,1,'{username}')"
        try:
            cursor.execute(sql)
            connection.commit()
        except:
            print(sql)
            return redirect('signup?dberr=true')
        sql=f"SELECT prof_id FROM User_Profile WHERE login='{email}'"
        try:
            cursor.execute(sql)
        except:
            return redirect('signup?dberr=true')
        session['user_id']=cursor.fetchall()[0][0]
        connection.close()
        return redirect('main')
    else:
        return render_template('signup.html')
    
@app.route("/logout", methods=['GET','POST'])
def logout():
    if request.method=='POST':
        session.pop('user_id', None)
        return redirect(url_for('logup'))
    return render_template('logout.html')

@app.route("/books/<bookID>")
def book(bookID):
    if 'user_id' not in session:
        return redirect('/')
    try:
        connection=connect()
        cursor=connection.cursor()
        sql=f"SELECT * from Books WHERE book_id={bookID}"
        cursor.execute(sql)
        result=cursor.fetchall()
        title=result[0][1]
        author_id=result[0][2]
        genre_id=result[0][3]
        description=result[0][4]
        pdate=result[0][5]
        link=result[0][6]
        print(link)
        sql=f"SELECT author_name FROM Authors WHERE author_id={author_id}"
        cursor.execute(sql)
        author=cursor.fetchall()[0][0]
        sql=f"SELECT genre_name FROM Genres WHERE genre_id={genre_id}"
        cursor.execute(sql)
        genre=cursor.fetchall()[0][0]
    except:
        return "<h3>an error occured</h3>"
    return render_template('book.html', title=title, author=author, genre=genre, description=description, pdate=pdate, link=link)

#Главная страница с книгами
@app.route("/main", methods=['GET','POST'])
def main():
    if 'user_id' not in session:
        return redirect('/')
    if request.method=="POST":
        searchstr=request.form['search']
        return redirect(f'/main?search={urllib.parse.quote(searchstr)}')
    try:
            connection = connect()
            cursor=connection.cursor()
    except:
            pass
    search=request.args.get('search')
    if search:
        sql="SELECT * FROM Books WHERE book_name LIKE %s OR description LIKE %s"
        print(sql)
        cursor.execute(sql,("%"+search+"%","%"+search+"%"))
        books=cursor.fetchall()
        links=[]
        for book in books:
            links.append('books/'+str(book[0]))
        return render_template("main.html", books=books, links=links)
    return render_template("main.html")