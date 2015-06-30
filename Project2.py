import re
from copy import deepcopy
import os
from flask import Flask, request, redirect, url_for, render_template, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.dialects import mysql
from datetime import datetime
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://WebLab:123456@fdu.nxtinc.cf/WebProject2'
db = SQLAlchemy(app)


class User(db.Model):
	uid = db.Column(db.Integer, primary_key=True)
	username = db.Column(mysql.TINYTEXT)
	email = db.Column(mysql.TINYTEXT)
	password = db.Column(mysql.TINYTEXT)
	avatar = db.Column(mysql.TINYTEXT)
	motto = db.Column(mysql.TEXT)
	questions = db.Column(mysql.TEXT)
	questions_n = db.Column(db.Integer)
	answers = db.Column(mysql.TEXT)
	answers_n = db.Column(db.Integer)
	followed = db.Column(mysql.TEXT)
	followed_n = db.Column(db.Integer)
	following = db.Column(mysql.TEXT)
	following_n = db.Column(db.Integer)

	def __init__(self, username, email, password):
		self.username = username
		self.email = email
		self.password = password
		self.avatar = 'head-default.jpg'
		self.motto = ''
		self.questions = '[]'
		self.answers = '[]'
		self.following = '[]'
		self.followed = '[]'
		self.questions_n = 0
		self.answers_n = 0
		self.following_n = 0
		self.followed_n = 0

	def have_unread_msg(self):
		return 0 != Message.query.filter_by(to_uid=self.uid, checked=False).count()

	def __repr__(self):
		return '<User {} email: {} Q: {} A: {} Fd: {} Fi: {}>'.format(
			self.username, self.email, len(json.loads(self.questions)), len(json.loads(self.answers)),
			len(json.loads(self.followed)), len(json.loads(self.following))
		)

	def get_followeds(self):
		his_followed_id = json.loads(self.followed)
		his_followed = []
		for uid in his_followed_id:
			his_followed.append(get_user_by_id(uid))
			his_followed.reverse()
		return his_followed

	def get_followings(self):
		his_following_id = json.loads(self.following)
		his_following = []
		for uid in his_following_id:
			his_following.append(get_user_by_id(uid))
			his_following.reverse()
		return his_following


class Question(db.Model):
	qid = db.Column(db.Integer, primary_key=True)
	title = db.Column(mysql.TEXT)
	content = db.Column(mysql.TEXT)
	ask_user = db.Column(mysql.TINYTEXT)
	time = db.Column(mysql.TINYTEXT)
	active_time = db.Column(mysql.TINYTEXT)
	answers = db.Column(mysql.TEXT)
	answers_n = db.Column(db.Integer)

	def __init__(self, title, content, asker, ask_time):
		self.title = title
		self.content = content
		self.ask_user = asker
		self.time = ask_time
		self.active_time = ask_time
		self.answers = '[]'
		self.answers_n = 0

	def __repr__(self):
		return '<Question {}, ans_n={}>'.format(self.title, self.answers_n)


class Answer(db.Model):
	aid = db.Column(db.Integer, primary_key=True)
	answerer = db.Column(mysql.TINYTEXT)
	time = db.Column(mysql.TINYTEXT)
	answer_qid = db.Column(db.Integer)
	content = db.Column(mysql.TEXT)
	comments = db.Column(mysql.TEXT)

	def __init__(self, answerer, time, answer_qid, content):
		self.answerer = answerer
		self.time = time
		self.content = content
		self.answer_qid = answer_qid
		self.comments = '[]'
		self.comments_n = 0
		get_question_by_id(answer_qid).active_time = time


class Message(db.Model):
	mid = db.Column(db.Integer, primary_key=True)
	from_uid = db.Column(db.Integer)
	to_uid = db.Column(db.Integer)
	msg = db.Column(mysql.TEXT)
	time = db.Column(db.Integer)
	checked = db.Column(db.Boolean)

	def __init__(self, from_uid, to_uid, msg, time):
		self.from_uid = from_uid
		self.to_uid = to_uid
		self.msg = msg
		self.time = time
		self.checked = False


def get_username(email):
	return User.query.filter_by(email=email).first().username


def get_user_by_username(username):
	return User.query.filter_by(username=username).first()


def get_user_by_email(email):
	return User.query.filter_by(email=email).first()


def get_user_by_id(uid):
	return User.query.get(uid)


def get_answer_by_id(aid):
	return Answer.query.get(aid)


def get_question_by_id(qid):
	return Question.query.get(qid)


def get_hot_users(n):
	return User.query.order_by(User.followed_n.desc()).limit(n).all()


def get_hot_questions(n):
	return Question.query.order_by(Question.answers_n.desc()).limit(n).all()


def get_current_time():
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def sort_activities(activity):
	return activity['time']


def get_activity(cur_user):
	followings = cur_user.get_followings()
	activities = []
	for user in followings:
		questions = Question.query.filter_by(ask_user=user.username).all()
		answers = Answer.query.filter_by(answerer=user.username).all()
		activity = {}
		for a in answers:
			activity.clear()
			activity['qid'] = a.answer_qid
			activity['title'] = get_question_by_id(a.answer_qid).title
			activity['answer'] = a.content
			activity['answerer'] = user.username
			activity['time'] = a.time
			activities.append(deepcopy(activity))

		for q in questions:
			activity.clear()
			activity['qid'] = q.qid
			activity['title'] = q.title
			activity['asker'] = user.username
			activity['time'] = q.time
			activities.append(deepcopy(activity))
	activities = sorted(activities, key=lambda k: k['time'], reverse=True)
	return activities


@app.route('/')
def index():
	if 'username' in session:
		cur_user = get_user_by_username(session['username'])
		activities = get_activity(cur_user)
		return render_template('index.html', cur_user=cur_user, hot_users=get_hot_users(3),
							   hot_questions=get_hot_questions(3),
							   activities=activities, get_q=get_question_by_id)
	else:
		return render_template('login.html', hot_users=get_hot_users(8), hot_questions=get_hot_questions(8))


@app.route('/static/<path:path>')
def static_files(path):
	return app.send_static_file(path)


def login_valid(email, password):
	cur_user = User.query.filter_by(email=email).first()
	if cur_user is None:
		return False
	if (not re.match('^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email)) \
			or (len(password) < 6) \
			or (len(password) > 16) \
			or password.isdigit():
		return False
	return cur_user.password == password


@app.route('/login', methods=['POST'])
def login():
	if login_valid(request.form['email'], request.form['password']):
		session['username'] = get_user_by_email(request.form['email']).username
		return 'true'
	else:
		return 'rejected', 400


@app.route('/logout', methods=['GET'])
def logout():
	if 'username' in session:
		session.pop('username')
	return redirect(url_for('index'))


def check_valid_signup(cur_user):
	if User.query.filter_by(email=cur_user.email).all() \
			or User.query.filter_by(username=cur_user.username).all() \
			or (not re.match('^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', cur_user.email)) \
			or (len(cur_user.password) < 6) \
			or (len(cur_user.password) > 16) \
			or (len(cur_user.username) < 2) \
			or (len(cur_user.username) > 16) \
			or cur_user.password.isdigit():
		return False
	return True


@app.route('/signup', methods=['POST'])
def signup():
	cur_user = User(request.form['username'], request.form['email'], request.form['password'])
	if check_valid_signup(cur_user):
		db.session.add(cur_user)
		db.session.commit()
		session['username'] = request.form['username']
		return 'true'
	return 'rejected', 400


@app.route('/search')
def search():
	q = request.args.get('q')
	if 'username' not in session or not q or q == '':
		return redirect(url_for('index'))
	result = User.query.filter(User.username.like('%' + q + '%')).all()
	result += Question.query.filter(Question.title.like('%' + q + '%')).all()
	return render_template('search.html', result=result, cur_user=get_user_by_username(session['username']),
						   hot_users=get_hot_users(3), hot_questions=get_hot_questions(3),
						   get_user=get_user_by_username)


@app.route('/user/<username>')
def user_page(username):
	if 'username' not in session:
		return redirect(url_for('index'))
	user = get_user_by_username(username)
	his_questions = []
	his_questions_qid = json.loads(user.questions)
	for qid in his_questions_qid:
		his_questions.append(get_question_by_id(qid))
	his_questions.reverse()
	his_answers = []
	his_answers_id = json.loads(user.answers)
	for aid in his_answers_id:
		his_answers.append(get_answer_by_id(aid))
	his_answers.reverse()
	user.his_questions = his_questions
	user.his_answers = his_answers
	return render_template('profile.html', cur_user=get_user_by_username(session['username']),
						   user=user, get_q=get_question_by_id)


@app.route('/user/<username>/follow', methods=['POST'])
def follow(username):
	user = get_user_by_username(username)
	cur_user = get_user_by_username(session['username'])
	operation = request.form['operation']
	if operation == 'follow':
		user_followed_id = json.loads(user.followed)
		if cur_user.uid not in user_followed_id:
			user_followed_id.append(cur_user.uid)
			user.followed = json.dumps(user_followed_id)
			user.followed_n = len(user_followed_id)

		cur_user_following_id = json.loads(cur_user.following)
		if user.uid not in cur_user_following_id:
			cur_user_following_id.append(user.uid)
			cur_user.following = json.dumps(cur_user_following_id)
			cur_user.following_n = len(cur_user_following_id)

		db.session.commit()
		return 'ok'
	elif operation == 'unfollow':
		user_followed_id = json.loads(user.followed)
		if cur_user.uid in user_followed_id:
			user_followed_id.remove(cur_user.uid)
			user.followed = json.dumps(user_followed_id)
			user.followed_n = len(user_followed_id)

		cur_user_following_id = json.loads(cur_user.following)
		if user.uid in cur_user_following_id:
			cur_user_following_id.remove(user.uid)
			cur_user.following = json.dumps(cur_user_following_id)
			cur_user.following_n = len(cur_user_following_id)

		db.session.commit()
		return 'ok'
	else:
		return 'rejected', 400


@app.route('/discovery')
def discovery_page():
	if 'username' not in session:
		return redirect(url_for('index'))
	all_questions = Question.query.order_by(Question.active_time.desc()).all()
	for i in all_questions:
		if i.answers_n != 0:
			answers_id = json.loads(i.answers)
			i.latest_answer = get_answer_by_id(answers_id[-1])
	return render_template('discovery.html', cur_user=get_user_by_username(session['username']),
						   all_questions=all_questions, hot_users=get_hot_users(3),
						   hot_questions=get_hot_questions(3), get_user=get_user_by_username)


@app.route('/question/<int:qid>')
def question_page(qid):
	if 'username' not in session:
		return redirect(url_for('index'))
	q = get_question_by_id(qid)
	if q is None:
		return render_template('404.html', cur_user=get_user_by_username(session['username']),
							   hot_users=get_hot_users(3),
							   hot_questions=get_hot_questions(3), get_user=get_user_by_username), 404
	answers_id = json.loads(q.answers)[:5]
	answers = []
	for i in answers_id:
		answers.append(get_answer_by_id(i))
		answers[-1].comments_n = len(json.loads(answers[-1].comments))
	finished = Answer.query.filter_by(answer_qid=qid).count() <= 5
	return render_template('question.html', cur_user=get_user_by_username(session['username']),
						   question=get_question_by_id(qid), answers=answers, finished=finished, hot_users=get_hot_users(3),
						   hot_questions=get_hot_questions(3), get_user=get_user_by_username)


@app.route('/question/new', methods=['POST'])
def new_question():
	if request.form['title'] == '':
		return 'rejected', 400
	new_q = Question(request.form['title'], request.form['content'], session['username'], get_current_time())
	db.session.add(new_q)
	db.session.commit()
	asker = get_user_by_username(new_q.ask_user)
	user_questions_id = json.loads(asker.questions)
	user_questions_id.append(new_q.qid)
	asker.questions = json.dumps(user_questions_id)
	asker.questions_n = len(user_questions_id)
	db.session.commit()
	return str(new_q.qid)


@app.route('/question/<int:qid>/answer', methods=['POST'])
def answer_to(qid):
	cur_q = get_question_by_id(qid)
	operation = request.form['operation']
	if operation == 'answer':
		new_ans = Answer(session['username'], get_current_time(), qid, request.form['content'])
		if new_ans.content == '':
			return 'reject', 400
		db.session.add(new_ans)
		db.session.commit()
		cur_user = get_user_by_username(session['username'])

		answers = json.loads(cur_user.answers)
		answers.append(new_ans.aid)
		cur_user.answers = json.dumps(answers)
		cur_user.answers_n = len(answers)

		answers = json.loads(cur_q.answers)
		answers.append(new_ans.aid)
		cur_q.answers = json.dumps(answers)
		cur_q.answers_n = len(answers)

		db.session.commit()
		return render_template('answer_template.html', answers=[new_ans], get_user=get_user_by_username)
	elif operation == 'fetch':
		start = int(request.form['start'])
		answers = Answer.query.filter_by(answer_qid=qid).order_by(Answer.time.asc()).limit(start + 5).all()
		answers = answers[start:]
		finished = Answer.query.filter_by(answer_qid=qid).count() <= (start + 5)
		for i in answers:
			i.comments_n = len(json.loads(i.comments))
		return json.dumps({'dat': render_template('answer_template.html', answers=answers, get_user=get_user_by_username), 'finished': finished})
	else:
		return 'rejected', 400


@app.route('/answer/<int:aid>/comment', methods=['POST'])
def comment_to(aid):
	cur_answer = get_answer_by_id(aid)
	operation = request.form['operation']
	if operation == 'comment':
		if request.form['content'] == '':
			return 'rejected', 400
		new_comment = [session['username'], request.form['content'], get_current_time()]
		comments = json.loads(cur_answer.comments)
		comments.append(new_comment)
		cur_answer.comments = json.dumps(comments)
		db.session.commit()
		return render_template('comment_template.html', comments=[new_comment], get_user=get_user_by_username)
	elif operation == 'fetch':
		return render_template('comment_template.html', comments=json.loads(cur_answer.comments),
							   get_user=get_user_by_username)
	else:
		return 'rejected', 400


@app.route('/upload/image', methods=['POST'])
def upload_image():
	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], filename))
		return filename
	return 'rejected', 400


@app.route('/upload/avatar', methods=['POST'])
def upload_avatar():
	file = request.files['file']
	cur_user = get_user_by_username(session['username'])
	if file and allowed_file(file.filename):
		filename = session['username'] + '.avatar'
		file.save(os.path.join(app.config['UPLOAD_FOLDER_AVATAR'], filename))
		cur_user.avatar = filename + '?' + str(int(datetime.now().timestamp()))
		db.session.commit()
		return cur_user.avatar
	return 'rejected', 400


def allowed_file(filename):
	return '.' in filename and filename.lower().rsplit('.', 1)[1] in (['bmp', 'png', 'jpg', 'jpeg', 'gif'])


@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
	if 'username' not in session:
		return redirect(url_for('index'))
	cur_user = get_user_by_username(session['username'])
	if request.method == 'POST':
		password = request.form.get('password')
		motto = request.form.get('motto')
		if password is not None:
			if (len(password) < 6) or (len(password) > 16) or password.isdigit():
				return 'rejected', 400
			cur_user.password = password
		if motto is not None:
			cur_user.motto = motto
		db.session.commit()
		return 'ok'
	return render_template('settings.html', cur_user=cur_user)


@app.route('/message')
def message_page():
	if ('username' not in session) and (request.method == 'GET'):
		return redirect(url_for('index'))
	cur_user = get_user_by_username(session['username'])
	messages = Message.query \
		.filter(or_(Message.from_uid == cur_user.uid, cur_user.uid == Message.to_uid)) \
		.order_by(Message.time.asc()).all()
	history = {}
	for i in messages:
		if i.from_uid != cur_user.uid:
			history[i.from_uid] = [i.msg, i.time, False]
		else:
			history[i.to_uid] = [i.msg, i.time, False]
	history = sorted(history.items(), key=lambda k: k[1][1], reverse=True)
	for i in history:
		i[1][2] = 0 != Message.query.filter_by(from_uid=int(i[0]), to_uid=cur_user.uid, checked=False).count()
	return render_template('message.html', cur_user=cur_user, get_user=get_user_by_id, history=history)


@app.route('/message/<username>', methods=['GET', 'POST'])
def message(username):
	if request.method == 'GET':
		if (('username' not in session) and (request.method == 'GET')) or (session['username'] == username):
			return redirect(url_for('index'))
		cur_user = get_user_by_username(session['username'])
		user = get_user_by_username(username)
		chat = Message.query.filter_by(from_uid=user.uid, to_uid=cur_user.uid).all()
		for i in chat:
			i.checked = True
		db.session.commit()
		return render_template('chat.html', cur_user=cur_user, user=user, get_user=get_user_by_id, chat=chat)
	else:
		cur_user = get_user_by_username(session['username'])
		user = get_user_by_username(username)
		new_msg = Message(cur_user.uid, user.uid, request.form['msg'], get_current_time())
		db.session.add(new_msg)
		db.session.commit()
		return render_template('chatmsg_template.html', cur_user=cur_user, user=user, chat_msg=new_msg)


if __name__ == '__main__':
	app.secret_key = '.\xb8/\xc6a\xc4\xe2G\xc6\xc5;\x98\xbej\xa6\x8b\\\x1b:Ea\xc1\x17\xbd'
	app.config['UPLOAD_FOLDER_IMAGE'] = os.path.dirname(os.path.abspath(__file__)) + '\\static\\upload\\'
	app.config['UPLOAD_FOLDER_AVATAR'] = os.path.dirname(os.path.abspath(__file__)) + '\\static\\img\\avatar\\'
	app.run(debug=True)
