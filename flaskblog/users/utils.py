
import os
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture, name):
    pic_name = name
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = pic_name + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    i = Image.open(form_picture)
    output_size = (125, 125)
    i.thumbnail(output_size)
    width, height = i.size
    print(width, height)
    offset  = int(abs(height-width)/2)
    if width>height:
        i = i.crop((offset,0,width-offset,height))
    elif height>width:
        i = i.crop((0,offset,width,height-offset))
    i.save(picture_path)

    return picture_fn

def delete_picture(filename):
    picture_path = os.path.join(current_app.root_path, "static/profile_pics", filename)
    os.remove(picture_path)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='dmitrix_n@mail.ru',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
