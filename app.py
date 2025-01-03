from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username yang anda masukkan sudah ada', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful', 'success')
        return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        
        flash('Username atau password yang anda masukkan salah')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', users=users)

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    
    existing_user_by_username = User.query.filter_by(username=username).first()
    if existing_user_by_username:
        flash('Username yang anda masukkan sudah ada', 'danger')
        return redirect(url_for('add_user_page'))  

    existing_user_by_email = User.query.filter_by(email=email).first()
    if existing_user_by_email:
        flash('Email yang anda masukkan sudah terdaftar', 'danger')
        return redirect(url_for('add_user_page'))  

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    flash('User berhasil ditambahkan', 'success')
    return redirect(url_for('add_user_page'))


@app.route('/add_user_page')
@login_required
def add_user_page():
   return render_template('add_user.html')

@app.route('/edit_user/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    # ngambil data dari form
    new_username = request.form['username']
    new_email = request.form['email']
    
    existing_user_by_username = User.query.filter_by(username=new_username).first()
    if existing_user_by_username and existing_user_by_username.id != user.id:
        flash('Username yang anda masukkan sudah ada', 'danger')
        return redirect(url_for('edit_user_page', id=id))  

    existing_user_by_email = User.query.filter_by(email=new_email).first()
    if existing_user_by_email and existing_user_by_email.id != user.id:
        flash('Email yang anda masukkan sudah terdaftar', 'danger')
        return redirect(url_for('edit_user_page', id=id)) 

    if request.form.get('password'):
        user.set_password(request.form['password'])

    # Update data pengguna
    user.username = new_username
    user.email = new_email
    user.role = request.form['role']  

    db.session.commit()
    flash('User berhasil diupdate', 'success')
    return redirect(url_for('edit_user_page', id=id))

@app.route('/edit_user_page/<int:id>')
@login_required
def edit_user_page(id):
   user = User.query.get_or_404(id)
   return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)  
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('dashboard')) 

@app.route('/logout')
@login_required
def logout():
    session.clear()    
    return redirect(url_for('index'))  

if __name__ == '__main__':
    app.run(debug=True)