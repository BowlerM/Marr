from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, TextAreaField
from wtforms.validators import InputRequired, Email, Optional, Length

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired("Cannot be empty"), Email("Must be in form of email address")], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired("Cannot be empty")],render_kw={"placeholder": "Password"})


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired("Cannot be empty"), Length(max=32, message="Username must be <32 characters")], render_kw={"placeholder": "Username"})
    email = EmailField('Email', validators=[InputRequired("Cannot be empty"), Email("Must be in form of email address")], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired("Cannot be empty"), Length(max=32, message="Password must be <32 characters")],render_kw={"placeholder": "Password"})

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=50, message="Title must be <50 characters")], render_kw={"placeholder": "Title (not required)"})
    content = TextAreaField('Content', validators=[InputRequired("Cannot be empty"), Length(max=5000, message="Post must contain <5000 characters")], render_kw={"placeholder": "Content (5000 char limit)"})

class ChangeSettingsForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired("Cannot be empty"), Length(max=32, message="Username must be <32 characters")])
    email = EmailField('Email', validators=[InputRequired("Cannot be empty"), Email("Must be in form of email address")])
    password = StringField('Password', validators=[InputRequired("Cannot be empty"), Length(max=32, message="Password must be <32 characters")])

class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=50, message="Title must be <50 characters")])
    content = TextAreaField('Content', validators=[InputRequired("Cannot be empty"), Length(max=5000, message="Post must contain <5000 characters")])