from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flaskblog.models import User
from flask_wtf.file import FileField, FileAllowed


class UserForm(FlaskForm):
    nickname = StringField('Nickname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    picture = FileField("Profile picture", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField('Create a user')

    def validate_nickname(self, nickname):
        user = User.query.filter_by(nickname=nickname.data).first()
        if user:
            raise ValidationError('That nickname is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError("That name is taken.")
            
    def filter_nickname(form, nickname):
        return nickname.strip()

    def filter_name(form, name):
        return name.strip()


class UpdateUserForm(UserForm):
    submit = SubmitField("Update a user")
    password = None
    user_id = HiddenField("user_id", validators=[DataRequired()])

    def validate_email(self, email):
        if User.query.get(int(self.user_id.data)).email != email.data:
            return super().validate_email(email)

    def validate_name(self, name):
        if User.query.get(int(self.user_id.data)).name != name.data:
            return super().validate_name(name)

    def validate_nickname(self, nickname):
        if User.query.get(int(self.user_id.data)).nickname != nickname.data:
            return super().validate_nickname(nickname)

# class UpdateUserForm(FlaskForm):
#     nickname = StringField('Nickname',
#                            validators=[DataRequired(), Length(min=2, max=20)])
#     name = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
#     email = StringField('Email',
#                         validators=[DataRequired(), Email()])
#     picture = FileField("Profile picture", validators=[FileAllowed(["jpg", "png"])])
#     submit = SubmitField('Update user')


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class DeleteUserForm(FlaskForm):
    submit = SubmitField("Delete")
