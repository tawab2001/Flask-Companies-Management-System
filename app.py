from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///companies.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Company Model
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    employees_count = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)

# Company Form
class CompanyForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    employees_count = IntegerField('Number of Employees', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Routes
@app.route('/companies')
def list_companies():
    companies = Company.query.all()
    return render_template('companies.html', companies=companies)

@app.route('/company/<int:id>')
def view_company(id):
    company = Company.query.get_or_404(id)
    return render_template('company_detail.html', company=company)

@app.route('/company/create', methods=['GET', 'POST'])
def create_company():
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            description=form.description.data,
            employees_count=form.employees_count.data,
            location=form.location.data
        )
        db.session.add(company)
        db.session.commit()
        return redirect(url_for('list_companies'))
    return render_template('company_form.html', form=form)



# # LAB 1 
# '''
# create a company route that display all companies
# - company name
# - company location
# - company description
# - company employees count
# '''