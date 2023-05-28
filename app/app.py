from flask import Flask, render_template, request, redirect, url_for, session, flash
from orm import User, DBSession, Image
import os
import pandas as pd
import plotly.express as px

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
    UPLOAD_FOLDER = os.path.join(os.getcwd(),"static/uploads/")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB max upload size

app = Flask(__name__)
app.config.from_object(Config)

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_by_email(email)
        if user and user.password == password:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['logged_in'] = True
            flash('Logged in successfully')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))
    return render_template('login.html')

# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if User.get_by_email(email):
            flash('Email already exists')
            return redirect(url_for('register'))
        if not name or not email or not password:
            flash('Please fill all fields')
            return redirect(url_for('register'))
        user = User(name=name, email=email, password=password)
        user.save()
        flash('User created successfully')
        return redirect(url_for('login'))
    return render_template('register.html')

# logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# index
@app.route('/')
def index():
    if 'user_id' in session:
        save_image_to_folder(session['user_name'])
        emotion_data_path = os.path.join(app.config['UPLOAD_FOLDER'],f"emotions_{session['user_name']}", 'emotion.txt')
        if os.path.exists(emotion_data_path):
            emotion_data = pd.read_csv(emotion_data_path, names=['emotion', 'path', 'time'])
            # convert time to seconds
            emotion_data['time'] = pd.to_datetime(emotion_data['time'], format='%Y-%m-%d %H:%M:%S.%f')
            emotion_data['minutes'] = (emotion_data['time'] - emotion_data['time'].min()).dt.total_seconds() / 60
            fig = px.line(emotion_data, x='minutes', y='emotion', title='Emotion over time')
            common_emo = emotion_data['emotion'].value_counts()
            fig2 = px.bar(common_emo, x=common_emo.index, y='emotion', title='Common emotions')
        else:
            fig = None
            emotion_data = None
        return render_template('index.html', graph2=fig2.to_html(), graph=fig.to_html(), emotion_data=emotion_data.to_html())
    else:
        return redirect(url_for('login'))

def save_image_to_folder(name):
    if ' ' in name: # replace spaces with underscores
        name = name.replace(' ', '_')
    folder_name = f'emotions_{name}'
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        # touch the emotion.txt file
        with open(os.path.join(folder_path, 'emotion.txt'), 'w') as f:
            pass
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg') or file.endswith('.txt'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            if os.path.isfile(file_path):
                if os.path.exists(os.path.join(folder_path, file)):
                    # append from outer file to this file
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    with open(os.path.join(folder_path, file), 'a') as f:
                        for line in lines:
                            e,p,t = lines[0].split(',')
                            p = p.replace(r'static\uploads', f'static\\uploads\\{folder_name}')
                            print(p)
                            f.write(f'{e},{p},{t}')
                    # delete the outer file
                    os.unlink(file_path)
                else:
                    os.rename(file_path, os.path.join(folder_path, file))
                    # save it to the database
                    emotion = file.split('_')[0]
                    image = Image(user_id=session['user_id'], file_name=name, emotion=emotion, file_path=os.path.join(folder_name, file))
                    image.save()

if __name__ == '__main__':
    with app.app_context():
        DBSession().generate_all()


    app.run(debug=True, host='0.0.0.0')