from flask import Flask, request, redirect, render_template, session, flash, url_for, abort
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db, models


from .forms import LoginForm, RegisterForm, CreatePostForm, ChangeSettingsForm, EditPostForm
from .models import User, Posts, Likes


import uuid, datetime, json

@app.route('/', methods=['GET'])
def index():
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	posts = Posts.query.order_by(Posts.date.desc()).all()

	return render_template('index.html',
							title="Marr",
							user=current_user,
							posts=posts)

@app.route('/user/<id>', methods=['GET'])
def getUser(id):
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	user = User.query.filter_by(userID=id).first()

	if not user:
		flash('User does not exist', 'error')
		return(redirect(url_for('index')))

	#if you click on your own username on a post it will redirect you to your account
	if(user == current_user):
		return redirect(url_for('myaccount'))

	posts = user.posts.order_by(Posts.date.desc())

	return render_template('user.html',
							title=f"@{user.username}",
							user=user,
							posts=posts)

@app.route('/myaccount', methods=['GET'])
def myaccount():
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	posts = current_user.posts.order_by(Posts.date.desc())

	return render_template('myaccount.html',
							title=f"@{current_user.username}",
							user=current_user,
							posts=posts)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	form = ChangeSettingsForm()
	#without this check any data the user changes is overridden by the prepopulated data
	if request.method == 'GET':
		#prepopulates the form with users current data
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.password.data = current_user.password

	if form.validate_on_submit():
		newUsername = form.username.data
		newEmail = form.email.data
		newPassword = form.password.data

		#checks if username was attempted to be changed
		if newUsername != current_user.username:
			#gets the user with the username that the current user is trying to change theirs to
			checkuser = User.query.filter_by(username=newUsername).first()

			#if this user exists and the ID of them is not our current users ID
			#then the current user must be trying to change to a username that already exists
			if checkuser and checkuser.userID != current_user.userID:
				flash('Username already taken', 'error')
				return redirect(url_for('settings'))

		#checks if email was attempted to be changed
		if newEmail != current_user.email:
			#gets the user with the email that the current user is trying to change theirs to
			checkuser = User.query.filter_by(email=newEmail).first()

			#if this user exists and the ID of them is not our current users ID
			#then the current user must be trying to change to a email that already exists
			if checkuser and checkuser.userID != current_user.userID:
				flash('Email already used', 'error')
				return redirect(url_for('settings'))

		#update current users details
		current_user.username = newUsername
		current_user.email = newEmail
		current_user.password = newPassword
		db.session.commit()
		flash('Details changed', 'success')

	return render_template('settings.html',
							title="Settings",
							form=form,
							user=current_user)

@app.route('/delete-account', methods=['POST', 'GET'])
def deleteAccount():
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	#try catch implemented as user must go through proper process to delete their account so this prevents the user from going to /delete-account in their browser
	#as request.data will be empty unless they use the proper method entailed on the website
	try:
		data= json.loads(request.data)
		confirmed = bool(data.get('confirmed'))
	except:
		abort(400, 'Must confirm to delete account')

	if not confirmed:
		abort(400, 'Must confirm to delete account')

	#delete all the users posts and likes first to satisfy database
	#-----------------------------------------------
	for post in current_user.posts:
		db.session.delete(post)

	for like in current_user.likes:
		db.session.delete(like)
	#-----------------------------------------------

	#then delete the users account
	db.session.delete(current_user)
	db.session.commit()

	return json.dumps('status: OK')

@app.route('/favourites', methods=['GET'])
def favourites():
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	#first get users likes in descending order
	favposts = Likes.query.filter_by(userID=current_user.userID).order_by(Likes.date.desc()).all()

	#then get the corresponding posts
	posts= []
	for fav in favposts:
		posts.append(Posts.query.filter_by(postID=fav.postID).first())

	return render_template('favourites.html',
							title="Favourites",
							user=current_user,
							posts=posts)

@app.route('/createpost', methods=['GET', 'POST'])
def createpost():
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	form = CreatePostForm()
	if form.validate_on_submit():
		title = form.title.data
		content = form.content.data
		userId = current_user.userID

		#use uuid to generate a new id
		postId = str(uuid.uuid4())
		#keep generating ids until a unique one is generated (shouldnt be called often due to the sheer amount of possible ids)
		while(Posts.query.filter_by(postID=postId).first()):
			postId = str(uuid.uuid4())

		with app.app_context():
			#create new post
			newPost = Posts(postID=postId, userID=userId, title=title, content=content, date=datetime.datetime.utcnow())
			db.session.add(newPost)
			db.session.commit()

		flash('Post Created', 'success')
		return redirect(url_for('index'))
	return render_template('createpost.html',
						title="Create",
						form=form,
						user=current_user)

@app.route('/like', methods=['POST'])
def like():
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	data= json.loads(request.data)
	postId = str(data.get('postId'))

	post = Posts.query.filter_by(postID=postId).first()
	like = Likes.query.filter_by(userID=current_user.userID, postID=postId).first()

	if not post:
		abort(400,'Post does not exist')
	#if user has already liked the post
	elif like:
		#remove the like from the post
		db.session.delete(like)
		db.session.commit()
	#otherwise
	else:
		#add new like to the post
		like = Likes(userID=current_user.userID, postID=postId, date=datetime.datetime.utcnow())
		db.session.add(like)
		db.session.commit()

	return json.dumps({'status': 'OK', "likes": len(post.likes), "liked": current_user.userID in map(lambda x: x.userID, post.likes)})

@app.route('/delete-post/<id>', methods=['GET'])
def deletePost(id):
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	post = Posts.query.filter_by(postID=id).first()

	#prevents users from deleting posts that arent theirs
	if post.userID != current_user.userID:
		abort(400, 'Cannot delete this post')

	if not post:
		flash('Post does not exist', 'error')
		return redirect(url_for('index'))

	#delete all the post's likes first to satisfy database
	for like in post.likes:
		db.session.delete(like)

	#delete post
	db.session.delete(post)
	db.session.commit()
	flash('Post deleted', 'success')
	return redirect(url_for('index'))

@app.route('/edit-post/<id>', methods=['GET', 'POST'])
def editPost(id):
	#this is as a replacement for @login_required to redirect the user to the login page if they are not logged in
	if(not current_user.is_authenticated):
		return redirect(url_for('login'))

	post = Posts.query.filter_by(postID=id).first()

	#prevents users from editing posts that arent theirs
	if post.userID != current_user.userID:
		abort(400, 'Cannot edit this post')

	if not post:
		flash('Post does not exist', 'error')
		return redirect(url_for('index'))

	form = EditPostForm()
	#without this check any data the user changes is overridden by the prepopulated data
	if request.method == 'GET':
		#prepoulate form with posts current content
		form.title.data = post.title
		form.content.data = post.content

	if form.validate_on_submit():
		#change details of post
		post.title = form.title.data
		post.content = form.content.data
		post.edited = True
		db.session.commit()
		flash('Details changed', 'success')

		return redirect(url_for('index'))

	return render_template('editpost.html',
							user=current_user,
							post=post,
							form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password.data

		user = User.query.filter_by(email=email).first()

		#check user has entered right details
		if not user or password != user.password:
			flash('Please check login details and try again', 'error')
			return redirect('/login')

		#login user
		login_user(user, remember=True)
		return redirect(url_for('index'))
	return render_template('login.html',
							form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		username = form.username.data
		email = form.email.data
		password = form.password.data

		#check if an account with the email entered by the user already exists
		user = User.query.filter_by(email=email).first()
		if user:
			flash('Email already used', 'error')
			return redirect('/login')

		#check if an account with the username entered by the user already exists
		user = User.query.filter_by(username=username).first()
		if user:
			flash('Username taken', 'error')
			return redirect('/register')

		#use uuid to generate a new user id
		userId = str(uuid.uuid4())
		#keep generating ids until a unique one is generated (shouldnt be called often due to the sheer amount of possible ids)
		while(User.query.filter_by(userID=userId).first()):
			userId = str(uuid.uuid4())

		#create new user
		with app.app_context():
			user = models.User(userID=userId, username=username, email=email, password=password)
			db.session.add(user)
			db.session.commit()

		flash('Registered account successfully', 'success')
		#redirect user to login so they can login into their newly created account (quality of life)
		return redirect('/login')
	return render_template('register.html',
							form=form)

@app.route("/logout")
@login_required
def logout():
	#logs out the current user
	logout_user()
	return redirect('/login')