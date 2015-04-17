from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin
from flask import Flask, url_for, redirect, render_template, request
from app.models import *
from app import app,db
from wtforms import form, fields, validators
import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose

#class for overriding ModelView methods to make ModelView Work
class ActivityView(ModelView):
    def create_model(self,form):
        try:
            activity = Activity(name=form.data['name'])
            self.session.add(activity)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
    def update_model(self, form, model):
        try:
            model.name = form.data['name']
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
    def delete_model(self,model):
        try:
            self.on_model_delete(model)
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
    def is_accessible(self):
        return login.current_user.is_authenticated()
        
class QuestionView(ModelView):
    def create_model(self, form):
        try:
            question = Question(form.data["activity"],
                                form.data["question"],
                                form.data["unit_type"],
                                form.data["min_value"],
                                form.data["max_value"])
            self.session.add(question)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
    def update_model(self,form,model):
        try:
            model.question = form.data["question"]
            model.unit_type = form.data["unit_type"]
            self.session.commit()
        except:
            self.session.rollback()
            return Flase
        return True
        
    def delete_model(self,model):
        try:
            self.on_model_delete(model)
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
    def is_accessible(self):
        return login.current_user.is_authenticated()
        
class MyAdminIndexView(admin.AdminIndexView):
    @expose("/")
    def index(self):
        """
        if not login.current_user.is_authenticated():
            return redirect(url_for(".login_view"))
        return super(IndexView, self).index()
        """
        return "wow"
        
    @expose("/login", methods=("GET","POST"))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)
            
    @expose("/logout")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))
        
class AdminUser(db.Model):
    __tablename__ = "admin_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    salt = db.Column(db.String(32), nullable=False)

    __table_args__ = (UniqueConstraint("username"),)
    
    def __init__(self,username,password):
        sha256 = hashlib.sha256()
        self.username = username
        self.salt = os.urandom(32)
        sha256.update(self.salt)
        sha256.update(password)
        self.password = sha256.digest()
        
    def check_pass(self, password):
        sha256 = hashlib.sha256()
        sha256.update(self.salt)
        sha256.update(password)
        return self.password == sha256.digest()
    
    def is_authenticated(self):
        return True
        
    def is_active(self):
        return True
        
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return self.id
        
    def __unicode__(self):
        return self.username
        
# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not user.check_pass(self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return AdminUser.query.filter(AdminUser.username==self.login.data).first()
        
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app()
    
    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(user_id)
        
admin = Admin(app, index_view=MyAdminIndexView(), base_template="my_master.html")
admin.add_view(ActivityView(Activity, db.session))
admin.add_view(QuestionView(Question, db.session))
