from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import exc

from main import app
from forms import LoginForm, RegisterForm
from database import db, User

# object that tracks if were logged in 
login_manager = LoginManager()      # login = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  # manager needs to know where to redirect in case of no login


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('already logged in, {}'.format(current_user))
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():   
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not check_password_hash(user.password, form.password.data):
            flash('invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)       # stores user under current_user
        return redirect('/')                                # theres an option to extract info from next_page = request.args.get('next') and go there
    else:
        flash('incorrect passes')

    return render_template('login.html', form=form)

# new_item = StocksItems(symbol=symbol, count=count)
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    # if request.method == 'POST': # pytanie - czy można użyć tego?
    if form.validate_on_submit():   
        hashed_password = generate_password_hash(form.password.data, method='sha256')   
        new_user = User(email=form.email.data, username=form.username.data, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return '<h3>new user has been cerated<h3>' # now route to dashboard
        except exc.IntegrityError:# as e:
            return 'one of params not uniqu.    <a href="/signup">go back</a>       '#+'\n'+str(e)
    
        
    return render_template('signup.html', form=form)

@login_manager.user_loader
def load_user(user_id): # User Loader Function # for given id retreives user object
    return User.query.get(int(user_id)) # extension expects that the application will configure a
                            # user loader function, that can be called to load a user given the ID

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))