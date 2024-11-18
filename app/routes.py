# app/routes.py
from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from app import db  
from sqlalchemy import text

bp = Blueprint('main', __name__)

# Implementatoin Login functionality
@bp.route('/', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # print(username)
        # print(password)

        # Verify Username and Password from database
        sql = text("SELECT user_password, role_id, user_id FROM users WHERE user_name = :username")
        result = db.session.execute(sql, {'username': username}).fetchone()

        if result and result[0] == password:
            # If username exists and password matches, return home page
            session['username'] = username
            session['user-id'] = result[2]
            session['role-id'] = result[1]

            return redirect(url_for('main.Home'))
        else:
            # Invalid credentials, show error page
            error_message = "Invalid Credentials, please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role']
        
        # Check if the username already exists
        existing_user = db.session.execute(text("SELECT * FROM users WHERE user_name = :username"), {'username': username}).fetchone()
        if existing_user:
            flash("Username already exists!", "error")
            return redirect(url_for('main.signup'))
        
        # Insert into the users table
        sql = text("INSERT INTO users (user_name, user_password, role_id) VALUES (:username, :password, :role_id)")
        db.session.execute(sql, {'username': username, 'password': password, 'role_id': role_id})
        db.session.commit()

        # Redirect to login page after successful signup
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('main.Login'))

    # For GET requests, retrieve the available roles
    roles = db.session.execute(text("SELECT * FROM roles")).fetchall()
    return render_template('signup.html', roles=roles)


#Home Page
@bp.route('/home')
def Home():
    news_item = db.session.execute(text("select news_id, news_title from news")).fetchall()

    # print(news_item)
    return render_template('home.html', news_items=news_item)


@bp.route('/news/<int:news_id>')
def NewsDetails(news_id):

    sql = text('''select news.news_id,  news.news_title, news.news_body, news.created_at, news.status_id, news.user_id,news.news_id, news.news_title, count(likes.like_id) AS likes from news  
               join likes on news.news_id = likes.news_id 
                where news.news_id  = :news_id''')
    news_detail = db.session.execute(sql, {"news_id": news_id}).fetchone()

    # Query to get Author Name
    author_name_sql = text("select users.user_name from news join users ON news.user_id = users.user_id where news_id = :news_id;")
    author = db.session.execute(author_name_sql, {"news_id": news_id}).fetchone()

    # Query to get Comment of the News
    comment_sql = text('''select comments.comment_body, users.user_name
                    from news 
                    join comments on news.news_id = comments.news_id 
                    join users on comments.user_id = users.user_id 
                    where news.news_id = :news_id''')
    comments = db.session.execute(comment_sql, {"news_id": news_id}).fetchall()

    return render_template('news.html', news = news_detail, author = author, comments = comments)

@bp.route("/news/<int:news_id>/comment", methods=["POST"])
def post_comment(news_id):

    user_id = session['user-id']    
    # Get comment body from HTML Form
    comment_body = request.form['comment']
    # Write SQL query and execute to insert this comment inside database
    sql = text('INSERT INTO comments (user_id, news_id, comment_body) VALUES (:user_id, :news_id, :comment_body)')
    db.session.execute(sql, {'user_id': user_id, 'news_id': news_id, 'comment_body': comment_body})
    db.session.commit()

    # Redirect user back to the news 
    return redirect(url_for('main.NewsDetails', news_id = news_id))


@bp.route("/news/<int:news_id>/like", methods=["POST"])
def post_like(news_id):
    user_id = session['user-id']  

    #check if user has already liked that or not
    sql = text('SELECT 1 FROM likes WHERE user_id = :user_id AND news_id = :news_id')

    existing_like = db.session.execute(sql, {'user_id': user_id, 'news_id': news_id}).fetchone()

    if (existing_like):
        pass
    else:
        sql = text('INSERT INTO likes (user_id, news_id) VALUES (:user_id, :news_id )')
        db.session.execute(sql, {'user_id': user_id, 'news_id': news_id })
        db.session.commit() 

    return redirect(url_for('main.NewsDetails', news_id = news_id))




