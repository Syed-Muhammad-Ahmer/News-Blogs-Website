# app/routes.py
from flask import render_template, Blueprint, request, redirect, url_for, flash, session, abort
from app import db  
from sqlalchemy import text
from functools import wraps
from flask_ckeditor import CKEditor

bp = Blueprint('main', __name__)

# Role-based access control decorator
def role_required(role_id):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'role-id' not in session:
                flash("You must log in first.", "error")
                return redirect(url_for('main.Login'))
            if session['role-id'] != role_id:
                abort(403)  # Forbidden access
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# Implementatoin Login functionality
@bp.route('/', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verify Username and Password from database
        sql = text("SELECT user_password, role_id, user_id FROM users WHERE user_name = :username")
        result = db.session.execute(sql, {'username': username}).fetchone()

        if result and result[0] == password:
            # If username exists and password matches, return home page
            session['username'] = username
            session['user-id'] = result[2]
            session['role-id'] = result[1]
            print(result)
            if result[1] == 1:
                return redirect(url_for('main.HomeAdmin'))
            elif result[1] == 2:
                return redirect(url_for('main.HomeJournlist'))
            else:
                return redirect(url_for('main.HomeVisitor'))
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

################################### Home Pages ######################################

#Home Page for Visitor
@bp.route('/home_visitor')
@role_required(3)
def HomeVisitor():
    if 'username' not in session:
        return redirect(url_for('main.Login'))

    news_item = db.session.execute(
        text("SELECT news.news_id, news.news_body, news.news_title FROM news WHERE status_id = '2'")
    ).fetchall()

    return render_template('home.html', news_items=news_item)

#Home Page for Admin
@bp.route('/home_admin')
@role_required(1)
def HomeAdmin():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('main.Login'))

    # Fetch pending posts for approval
    pending_posts = db.session.execute(
        text("SELECT news.news_id, news.news_body, news.news_title FROM news WHERE status_id = '1'")
    ).fetchall()

    # Fetch all approved posts (for admin to interact like a subscriber)
    approved_posts = db.session.execute(
        text("SELECT news.news_id, news.news_body, news.news_title FROM news WHERE status_id = '2'")
    ).fetchall()

    # Pass both pending and approved posts to the template
    return render_template(
        'AdminHome.html',
        pending_posts=pending_posts,
        posts=approved_posts  # Matches the variable in the template
    )


#Home Page for journlist
@bp.route('/home_journalist')
@role_required(2)
def HomeJournlist():
    if 'username' not in session:
        return redirect(url_for('main.Login'))

    news_item = db.session.execute(
        text("SELECT news.news_id, news.news_body, news.news_title FROM news WHERE status_id = '2'")
    ).fetchall()
    # print(news_item)
    return render_template('journalistHome.html', all_news=news_item)


######################################Common  Functionaliteis #################################

###################### News Detials Page ####################

@bp.route('/news/<int:news_id>')
def NewsDetails(news_id):

    sql = text('''select news.news_id,  news.news_title, news.news_body, news.created_at, news.status_id, news.user_id,news.news_id, news.news_title, count(likes.like_id) AS likes from news  
               left join likes on news.news_id = likes.news_id 
                where news.news_id  = :news_id''')
    news_detail = db.session.execute(sql, {"news_id": news_id}).fetchone()
    print(news_id)
    print(news_detail)
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


@bp.route("/logout", methods=["POST"])
def logout():
    # Clear the user session
    session.pop("user_id", None)
    session.pop("user_name", None)
    
    # Flash message (optional)
    flash("You have been logged out successfully.", "success")
    
    # Redirect to the login page
    return redirect(url_for("main.Login"))


##################### Approve Post - Admin ##################
@bp.route('/admin/approve/<int:news_id>', methods=['POST'])
def approve_post(news_id):
    # Check if the user is an admin
    if 'username' not in session or session.get('role-id') != 1:
        return redirect(url_for('main.Login'))

    # Get the status_id for "approved" from the newsStatus table
    try:
        status_result = db.session.execute(
            text("SELECT status_id FROM newsStatus WHERE status_name = 'Published'")
        ).fetchone()

        if not status_result:
            flash("Approved status not found.", "error")
            return redirect(url_for('main.HomeAdmin'))

        approved_status_id = status_result[0]

        # Update the post status in the database
        db.session.execute(
            text("UPDATE news SET status_id = :status_id WHERE news_id = :news_id"),
            {'status_id': approved_status_id, 'news_id': news_id}
        )
        db.session.commit()
        flash("Post Approved Successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while approving the post: {str(e)}", "error")

    # Redirect back to the admin home page
    return redirect(url_for('main.HomeAdmin'))


@bp.route('/journalist/add_news', methods=['POST'])
def AddNews():
    if 'username' not in session or session['role-id'] != 2:
        flash("Access denied.")
        return redirect(url_for('main.Login'))
    # Fetch user ID from session
    user_id = session['user-id']
    news_title = request.form['news_title']
    news_body = request.form['news_body']

    try:
        # Add news with status as 'pending'
        db.session.execute(
            text('''INSERT INTO news (news_title, news_body, status_id, user_id)
                  VALUES (:news_title, :news_body, 
                 (SELECT status_id FROM newsStatus WHERE status_name = 'Draft'), :user_id)'''),
            {'news_title': news_title, 'news_body': news_body, 'user_id': user_id}
        )
        db.session.commit()
        flash("News submitted successfully and is pending approval.")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while adding news: {str(e)}")

    return redirect(url_for('main.HomeJournlist'))


@bp.route('/journalist/add_news', methods=['GET', 'POST'])
def add_news():
    # Check if the journalist is logged in
    if 'username' not in session:  # Assuming '2' is the journalist role
        flash('You need to log in as a journalist to access this page.', 'error')
        return redirect(url_for('main.Login'))
    
    if request.method == 'POST':
        # Retrieve form data
        news_title = request.form.get('news_title')
        news_body = request.form.get('news_body')
        
        # Validate input
        if not news_title or not news_body:
            flash('All fields are required!', 'error')
            return render_template('add_news.html')

        # Insert the news as a draft (status_id = 1)
        try:
            query = """
                INSERT INTO news (news_title, news_body, status_id, user_id)
                VALUES (:news_title, :news_body, :status_id, :user_id)
            """
            db.session.execute(query, {
                'news_title': news_title,
                'news_body': news_body,
                'status_id': 1,  # 1 represents a draft status
                'user_id': session['user_id']  # Assuming user_id is stored in the session
            })
            db.session.commit()
            flash('News added successfully!', 'success')
            return redirect(url_for('home_journalist'))  # Redirect to the journalist's home page
        except Exception as e:
            flash('An error occurred while adding the news. Please try again.', 'error')
            print(f"Error: {e}")

    # Render the Add News page for GET requests
    return render_template('add_news.html')
