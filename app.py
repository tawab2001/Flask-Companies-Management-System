from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///companies.db"
app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


# Company Model
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employees_count = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)


# Company Form
class CompanyForm(FlaskForm):
    name = StringField("Company Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    employees_count = IntegerField("Number of Employees", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Routes
@app.route("/companies")
def list_companies():
    companies = Company.query.all()
    return render_template("companies.html", companies=companies)


@app.route("/company/<int:id>")
def view_company(id):
    company = Company.query.get_or_404(id)
    return render_template("company_detail.html", company=company)


@app.route("/company/create", methods=["GET", "POST"])
def create_company():
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            description=form.description.data,
            employees_count=form.employees_count.data,
            location=form.location.data,
        )
        db.session.add(company)
        db.session.commit()
        return redirect(url_for("list_companies"))
    return render_template("company_form.html", form=form)


# Models
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def _repr_(self):
        return f"Job('{self.title}', '{self.company}', '{self.location}')"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


@app.route("/jobs")
def list_():
    jobs = Job.query.all()
    return render_template("job.html", jobs=jobs)


@app.route("/create_job", methods=["POST"])
def create_job():
    title = request.form.get("title")
    company = request.form.get("company")
    location = request.form.get("location")

    new_job = Job(title=title, company=company, location=location)
    db.session.add(new_job)
    db.session.commit()  # Commit the session to save the new job

    return "Job created successfully!"


@app.route("/update/job/<job_id>", methods=["PUT"])
def update_job(job_id):
    jod = Job.query.get(job_id)
    company = request.form.get("company")
    jod.company = company
    db.session.commit()
    return "Job updated successfully!"


# forms
class JobCreationForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    company = StringField("Company", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField("Create Job")


@app.route("/create_job_form", methods=["GET", "POST"])
def create_job_form():
    form = JobCreationForm()
    if form.validate_on_submit():  # POST
        title = form.title.data
        company = form.company.data
        location = form.location.data

        new_job = Job(title=title, company=company, location=location)
        db.session.add(new_job)
        db.session.commit()

        return "Job created successfully!"

    return render_template("create_job.html", form=form)


@app.route("/api/jobs/list", methods=["GET"])
def list_jobs():
    jobs = Job.query.all()  # database objects
    # serialization: object > json
    data = [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
        }
        for job in jobs
    ]
    return jsonify(data), 200  # status code


@app.route("/api/jobs/<int:id>", methods=["GET"])
def job_details(id):
    job = Job.query.get_or_404(id)
    data = {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
    }

    return jsonify(data), 200


@app.route("/api/jobs/create", methods=["POST"])
def job_create():
    data = request.get_json()

    new_job = Job(
        title=data["title"], company=data["company"], location=data["location"]
    )
    db.session.add(new_job)
    db.session.commit()

    return jsonify({"message": "Job Created Successfully!"}), 201


@app.route("/api/jobs/update/<int:id>", methods=["PUT"])
def job_update(id):
    data = request.get_json()

    job = Job.query.get(id)
    job.title = data["title"]
    job.company = data["company"]
    job.location = data["location"]

    db.session.commit()

    return jsonify({"message": "Job Updated Successfully!"})


@app.route("/api/jobs/delete/<int:id>", methods=["DELETE"])
def delete_job(id):
    job = Job.query.get(id)

    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job Deleted Successfully!"})


# Auth
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "User Already Exists!"})
    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User Created Successfully!"}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data["username"]).first()

    if user and user.check_password(data["password"]):
        token = create_access_token(identity=str(user.id))

        return jsonify({"access_token": token}), 200

    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/api/auth/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    data = {"id": user.id, "username": user.username}
    return jsonify(data), 200


@app.route("/api/companies", methods=["GET"])
def api_list_companies():
    companies = Company.query.all()
    data = [{
        "id": company.id,
        "name": company.name,
        "description": company.description,
        "employees_count": company.employees_count,
        "location": company.location
    } for company in companies]
    return jsonify(data), 200

@app.route("/api/companies/<int:id>", methods=["GET"])
def api_get_company(id):
    company = Company.query.get_or_404(id)
    data = {
        "id": company.id,
        "name": company.name,
        "description": company.description,
        "employees_count": company.employees_count,
        "location": company.location
    }
    return jsonify(data), 200

@app.route("/api/companies", methods=["POST"])
@jwt_required()
def api_create_company():
    data = request.get_json()
    
    new_company = Company(
        name=data["name"],
        description=data["description"],
        employees_count=data["employees_count"],
        location=data["location"]
    )
    db.session.add(new_company)
    db.session.commit()
    
    return jsonify({"message": "Company created successfully"}), 201

@app.route("/api/companies/<int:id>", methods=["PUT"])
@jwt_required()
def api_update_company(id):
    company = Company.query.get_or_404(id)
    data = request.get_json()
    
    company.name = data.get("name", company.name)
    company.description = data.get("description", company.description)
    company.employees_count = data.get("employees_count", company.employees_count)
    company.location = data.get("location", company.location)
    
    db.session.commit()
    return jsonify({"message": "Company updated successfully"}), 200

@app.route("/api/companies/<int:id>", methods=["DELETE"])
@jwt_required()
def api_delete_company(id):
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    return jsonify({"message": "Company deleted successfully"}), 200

# LAB 1
"""
create a company route that display all companies
- company name
- company location
- company description
- company employees count
"""


# LAB 2:
"""
1.  Create Table for company:
    - id (primary key)
    - name
    - description
    - employees_count
    - location
2. create View-all and view-single and write apis for the company
3. use flask forms to create the company
"""

# sayed.shaaban.khalifa@gmail.com

# LAB 3
"""
1. Create CRUD Operations Apis For Company
2. make sure that only registerd users can do Create And Update And Delete on Company APIs
"""


# # LAB 1
# '''
# create a company route that display all companies
# - company name
# - company location
# - company description
# - company employees count
# '''
