from flask_wtf import FlaskForm; # type: ignore
from wtforms import Form, StringField, PasswordField, SubmitField, BooleanField, SelectField, FieldList, FormField, FloatField # type: ignore
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError; # type: ignore
from CropMaster.models import User;

class Signup_form(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)]);
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Enter Password', validators=[DataRequired(), Length(min=4, max=25)])
    confirm_password = PasswordField('Confirm Password Again', validators=[DataRequired(), EqualTo('password', message='passwords must match')])
    signup = SubmitField('Sign up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first();

        if user:
            raise ValidationError('user with the given email already exists');

class Login_form(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    Login = SubmitField('Login')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if not user:
            raise ValidationError("user with the given email doesn't exists, so signup and then try to login")
        
class choose_state_form(FlaskForm):
    crop = SelectField('Choose Your Crop', validators=[DataRequired()], choices=[]);
    state = SelectField('Choose Your State', validators=[DataRequired()], choices=[]);
    area = FloatField("Enter your farm's area in acres")
    proceed_further = SubmitField('Proceed Further')

class choose_district_form(FlaskForm):
    district = SelectField('Choose Appropriate district', validators=[DataRequired()], choices=[]);
    season = SelectField('Choose the appropriate season', validators=[], choices=[]);
    predict = SubmitField('Predict');