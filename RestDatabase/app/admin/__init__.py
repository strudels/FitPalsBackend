from flask.ext.admin.contrib.sqla import ModelView
from controllers.ActivityAPI import *

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
        
@login_manager.init_app(app)
def load_user(userid):
    return AdminUser.get(userid)
        
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # login and validate the user...
        login_user(user)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", form=form)

admin = Admin(app)
admin.add_view(ActivityView(Activity, db.session))
admin.add_view(QuestionView(Question, db.session))
