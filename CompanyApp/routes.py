import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from CompanyApp import app, db, bcrypt
from CompanyApp.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddEmployeeToProjectForm, PostForm
from CompanyApp.models import User, Post,Department, Dependent, Dept_Locations, Employee, Project, Works_On
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html", title = 'Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/employees")
@login_required
def employees():
    employeesData = Employee.query.all()
    return render_template('employees.html',title = 'Employees', employeesData = employeesData)

@app.route("/projects")
@login_required
def projects():
    projectsData = Project.query.all()
    return render_template('projects.html', title = 'Projects', projectsData = projectsData)

@app.route("/projectAssignment")
@login_required
def projectAssignment():
    result = Employee.query.join(Works_On, Employee.ssn == Works_On.essn).add_columns(Employee.fname, Employee.lname, Employee.ssn).join(Project, Works_On.pno == Project.pnumber).add_columns(Project.pnumber, Project.pname, Project.plocation)
    return render_template('projectAssignment.html', title = 'Project Assignment', data = result)

@app.route("/project/<projectNumber>", methods = ['GET', 'POST'])
@login_required
def project(projectNumber):
    form = AddEmployeeToProjectForm()
    if form.validate_on_submit():
        formSSN = form.employees.data
        work_on = Works_On(pno = projectNumber, essn = formSSN, hours = 0)
        db.session.add(work_on)
        db.session.commit()
        flash('Employee has been assigned to this project', 'success')
        return redirect(url_for('project', projectNumber = projectNumber))
    project = Project.query.get_or_404(projectNumber)
    Employees = Works_On.query.filter_by(pno = projectNumber).join(Employee).\
	add_columns(Employee.fname, Employee.lname, Employee.ssn)
    return render_template("project.html", title = 'Project Details', form = form, project = project, employees= Employees)

@app.route("/project/<projectNumber>/remove/<essn>", methods=['POST'])
@login_required
def removeEmployee(projectNumber, essn):
    projectAssignment = Works_On.query.filter_by(pno = projectNumber).filter_by(essn = essn).first()
    db.session.delete(projectAssignment)
    db.session.commit()
    flash('The employee has been removed from the project!', 'success')
    return redirect(url_for('project', projectNumber = projectNumber))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/dept/new", methods=['GET', 'POST'])
@login_required
def new_dept():
    form = DeptForm()
    if form.validate_on_submit():
        dept = Department(dname=form.dname.data, dnumber=form.dnumber.data,mgr_ssn=form.mgr_ssn.data,mgr_start=form.mgr_start.data)
        db.session.add(dept)
        db.session.commit()
        flash('You have added a new department!', 'success')
        return redirect(url_for('home'))
    return render_template('create_dept.html', title='New Department',
                           form=form, legend='New Department')


@app.route("/dept/<dnumber>")
@login_required
def dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    return render_template('dept.html', title=dept.dname, dept=dept, now=datetime.utcnow())


@app.route("/dept/<dnumber>/update", methods=['GET', 'POST'])
@login_required
def update_dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    print(dnumber)
 
    form = DeptUpdateForm()
    if form.validate_on_submit():          # notice we are are not passing the dnumber from the form
        dept.dname=form.dname.data
        dept.mgr_ssn=form.mgr_ssn.data
        dept.mgr_start=form.mgr_start.data
        db.session.commit()
        flash('Your department has been updated!', 'success')
        return redirect(url_for('dept', dnumber=dnumber))
    elif request.method == 'GET':              # notice we are not passing the dnumber to the form
        form.dname.data = dept.dname
        form.mgr_ssn.data = dept.mgr_ssn
        form.mgr_start.data = dept.mgr_start
    return render_template('create_dept.html', title='Update Department',
                           form=form, legend='Update Department')




@app.route("/dept/<dnumber>/delete", methods=['POST'])
@login_required
def delete_dept(dnumber):
    dept = Department.query.get_or_404(dnumber)
    db.session.delete(dept)
    db.session.commit()
    flash('The department has been deleted!', 'success')
    return redirect(url_for('home'))
