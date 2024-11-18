from . import db

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    role_name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<Role {self.role_name}>'


class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=True)
    
    # Define the relationship with the Role model
    role = db.relationship('Role', backref='users', lazy=True)

    def __repr__(self):
        return f'<User {self.user_name}>'
    

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=True)  # Foreign key from roles

    # Define the relationship with the Role model
    role = db.relationship('Role', backref='users', lazy=True)

    def __repr__(self):
        return f'<User {self.user_name}>'


class NewsStatus(db.Model):
    __tablename__ = 'newsStatus'
    
    status_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<NewsStatus {self.status_name}>'
    

class News(db.Model):
    __tablename__ = 'news'
    
    news_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    news_title = db.Column(db.String(100), nullable=False)
    news_boby = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Default current timestamp
    status_id = db.Column(db.Integer, db.ForeignKey('newsStatus.status_id'), nullable=False)  # Foreign key from newsStatus
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Foreign key from users

    # Define the relationships
    status = db.relationship('NewsStatus', backref='news', lazy=True)
    user = db.relationship('User', backref='news', lazy=True)

    def __repr__(self):
        return f'<News {self.news_title}>'
    

class Like(db.Model):
    __tablename__ = 'likes'
    
    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Foreign key from users
    news_id = db.Column(db.Integer, db.ForeignKey('news.news_id'), nullable=False)  # Foreign key from news

    # Define the relationships
    user = db.relationship('User', backref='likes', lazy=True)
    news = db.relationship('News', backref='likes', lazy=True)

    def __repr__(self):
        return f'<Like user_id={self.user_id} news_id={self.news_id}>'


class Comment(db.Model):
    __tablename__ = 'comments'
    
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Foreign key from users
    news_id = db.Column(db.Integer, db.ForeignKey('news.news_id'), nullable=False)  # Foreign key from news
    comment_body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Default current timestamp

    # Define the relationships
    user = db.relationship('User', backref='comments', lazy=True)
    news = db.relationship('News', backref='comments', lazy=True)

    def __repr__(self):
        return f'<Comment user_id={self.user_id} news_id={self.news_id}>'


class Multimedia(db.Model):
    __tablename__ = 'multimedia'
    
    multimedia_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paths = db.Column(db.String(100), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.news_id'), nullable=False)  # Foreign key from news

    # Define the relationship
    news = db.relationship('News', backref='multimedia', lazy=True)

    def __repr__(self):
        return f'<Multimedia news_id={self.news_id} paths={self.paths}>'
    