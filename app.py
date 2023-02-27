######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import sys

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'tony2000'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall() # Email of Users

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/accountExists", methods=['GET'])
def accountExists():
	return render_template('accountExist.html')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		dob=request.form.get('dob')
		fname=request.form.get('fname')
		lname=request.form.get('lname')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	
	cursor = conn.cursor()
	test = isEmailUnique(email) # Account is unique
	if test: 
		print(cursor.execute("INSERT INTO Users (email, password, dob, fname, lname, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, dob, fname, lname, hometown, gender)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else: # Already created account
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('accountExists'))


def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption, user_id FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def getPhotoId(imgdata):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Photos WHERE imgdata = %s", (imgdata))
	return cursor.fetchone()[0]

def getAlbumId(album_name):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE Name = '{0}' AND user_id = '{1}'".format(album_name, uid))
	return cursor.fetchone()[0]

def containsPhotos(album_id):
	cursor = conn.cursor()
	if cursor.execute("SELECT photo_id FROM Photos WHERE album_id = '{0}'".format(album_id)):
		return True
	else:
		return False

def getPhotosFromAlbum(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption, user_id FROM Photos WHERE album_id='{0}' ".format(album_id))
	return cursor.fetchall()

def getTagId(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_id FROM Tags WHERE name = '{0}'".format(tag))
	return cursor.fetchone()[0]

def AlbumExist(album_name):
	cursor = conn.cursor()
	if cursor.execute("SELECT album_id FROM Albums WHERE Name = '{0}'".format(album_name)):
		return True
	else:
		return False

#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tag = request.form.get('tags')
		album_name = request.form.get('album_name')
		photo_data = imgfile.read()
		cursor = conn.cursor()
		if (AlbumExist(album_name) == False):
			return render_template('upload.html', message='Album does not exist!')
		album_id = getAlbumId(album_name)

		#insert photo into database
		cursor.execute("INSERT INTO Photos(imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s)", (photo_data, uid, caption, album_id))
		conn.commit()

		cursor.execute("SELECT photo_id FROM Photos WHERE imgdata = %s", (photo_data))
		photoid = cursor.fetchone()[0]

	   
		#insert tags into database
		cursor.execute("INSERT INTO Tags(name) VALUES (%s)", (tag))

		tag_id = getTagId(tag)
		#Link tag and photo
		cursor.execute("INSERT INTO Tagged(photo_id, tag_id) VALUES (%s, %s)", (photoid, tag_id))
		conn.commit()

		return render_template('upload.html', message='Photo uploaded!')
	
	
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

# MY METHODS

#Search a friend
@app.route('/add_friends', methods=['GET', 'POST'])
@flask_login.login_required
def AddFriends():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		friend_email = request.form.get('friend_email')
		cursor = conn.cursor()
		
		if isEmailUnique(friend_email) == True:
			return render_template('add_friends.html', message = "Email does not exist!")
		else:
			friend_id = getUserIdFromEmail(friend_email)
			cursor.execute("SELECT UID2 FROM Friends WHERE UID1 = '{0}'".format(uid))
			data = cursor.fetchall()

			for i in data:
				if i[0] == friend_id:
					return render_template('add_friends.html', message = "Already friends!")

			cursor.execute("INSERT INTO Friends (UID1, UID2) VALUES ('{0}', '{1}')".format(uid, friend_id))
			conn.commit()
			
			return render_template('hello.html', message = "Added as friends!")
	else:
		return render_template('add_friends.html')

@app.route('/list_friends', methods=['GET'])
@flask_login.login_required
def ListFriends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT email, fname, lname FROM Users WHERE user_id IN (SELECT UID2 FROM Friends WHERE UID1 = '{0}')".format(uid))
	data = cursor.fetchall()
	return render_template('list_friends.html', message='Here are your friends', friends = data)

@app.route('/rec_friends', methods=['GET'])
def friendRec():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT email, fname, lname FROM Users Where user_id IN (SELECT DISTINCT f2.UID2 FROM Friends AS f1 JOIN Friends AS f2 ON f1.UID2 = f2.UID1 WHERE f1.UID1 = '{0}' AND f2.UID2 != f1.UID1)".format(uid))
	friends = cursor.fetchall()
	return render_template('rec_friends.html', message='Here are your recommended friends', friends = friends)

# Albums

@app.route('/create_album', methods=['GET', 'POST'])
@flask_login.login_required
def CreateAlbum():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		album_name = request.form.get('album_name')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums (user_id, Name) VALUES ('{0}', '{1}')".format(uid, album_name))
		conn.commit()

		return render_template('create_album.html', message = "Album created!")
	else:
		return render_template('create_album.html')
	
@app.route('/browse_album', methods=['GET' , 'POST'])
def BrowseAlbum():
	if request.method == 'POST':
		print("POST")
		userMail = request.form.get('userMail')
		uid = getUserIdFromEmail(userMail)
		cursor = conn.cursor()
		cursor.execute("SELECT Name, album_id FROM Albums WHERE user_id = '{0}'".format(uid))
		albums = cursor.fetchall()

		return render_template('choose_album.html', message='Here are your albums', albums = albums, uid = uid)
	
	return render_template('browse_album.html')

@app.route('/delete_album', methods=['GET', 'POST'])
@flask_login.login_required
def DeleteAlbum():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		album_name = request.form.get('album_name')
		album_id = getAlbumId(album_name)
		

		cursor = conn.cursor()
		cursor.execute("SELECT photo_id FROM Photos WHERE album_id = '{0}'".format(album_id))
		all_photos = cursor.fetchall()

		# Deletes all photo from album
		for i in range(len(all_photos)):
			temp = int(all_photos[i][0])
			DeletePhotos(temp)

		cursor.execute("DELETE FROM Albums WHERE user_id = '{0}' AND album_id = '{1}'".format(uid, album_id))
		conn.commit()

		return render_template('delete_album.html', message = "Album deleted!")
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT Name, album_id FROM Albums WHERE user_id = '{0}'".format(uid))
		albums = cursor.fetchall()
		return render_template('delete_album.html', message="Here are your albums", albums = albums)

# Photo methods

@app.route('/choose_album', methods=['GET', 'POST'])
def ShowPhotos():
	if request.method == 'POST':
		albumId = request.form.get('albumId')
		if containsPhotos(albumId) == False:
			return render_template('choose_album.html', message = "Album is empty!")
		
		photos = getPhotosFromAlbum(albumId)

		return render_template('show_photos.html', message='Here are your photos', photos = photos, base64=base64)
	
	return render_template('show_photos.html')

@app.route('/show_photos', methods=['GET', 'POST'])
@flask_login.login_required
def DeletePhotoFromView():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		photo_id = request.form.get('photo_id')
		# Check if User owns photo
		if checkPhotoOwner(photo_id, uid) == False:
			return render_template('show_photos.html', message = "You do not own this photo!", photos = getUsersPhotos(uid), base64=base64)
		DeletePhotos(photo_id)
		return render_template('show_photos.html', message = "Photo deleted! Here are your Photos.", photos = getUsersPhotos(uid), base64=base64)
	
	return render_template('show_photos.html', message="Here are your Photos." , photos = getUsersPhotos(uid), base64=base64)

def checkPhotoOwner(photo_id, uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Photos WHERE photo_id = '{0}'".format(photo_id))
	owner = cursor.fetchone()
	if owner[0] == uid:
		return True
	return False

def DeletePhotos(photo_id):
	cursor = conn.cursor()

	# Unlinks photoid from Tagged
	cursor.execute("DELETE FROM Tagged WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

	cursor.execute("SELECT tag_id FROM Tagged WHERE photo_id = '{0}'".format(photo_id))
	tags = cursor.fetchall() # All tags linked to photo

	for i in range(len(tags)):
		cursor.execute("DELETE FROM Tags WHERE tag_id ='{0}'".format(tags[i][0]))
		conn.commit()

	cursor.execute("DELETE FROM Photos WHERE photo_id='{0}'".format(photo_id))
	conn.commit()

# Tags Methods

def getPhotosFromTag(tags):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, name, caption, fname, lname FROM Users, Photos, Tags, Tagged WHERE Tags.tag_id = Tagged.tag_id AND Tagged.photo_id = Photos.photo_id AND Photos.user_id = Users.user_id AND Tags.name = '{0}'".format(tags))
	photos = cursor.fetchall()
	return photos

@app.route('/photo_by_tags', methods=['GET', 'POST'])
def PhotoByTag():
	if request.method == 'POST':
		tag = request.form.get('tag')
		photos = getPhotosFromTag(tag)

		return render_template('photo_by_tags.html', message="Here are the photos for this tag.", photos = photos, base64=base64)
	else:
		return render_template('photo_by_tags.html')

@app.route('/user_tags', methods=['GET', 'POST'])
@flask_login.login_required
def UserTags():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	if request.method == 'POST':
		tag = request.form.get('tag')
		photos = getPhotosFromTag(tag)
		return render_template('user_tags.html', message="Here are the photos for this tag.", photos = photos, base64=base64)
	else:
		return render_template('user_tags.html', tags = getUserTags())

def getUserTags():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT name FROM Tags, Tagged, Photos WHERE Tags.tag_id = Tagged.tag_id AND Tagged.photo_id = Photos.photo_id AND Photos.user_id = '{0}'".format(uid))
	tags = cursor.fetchall()
	return tags

@app.route('/popular_tags', methods=['GET', 'POST'])
def PopularTags():
	if request.method == 'POST':
		tag = request.form.get('tag')
		cursor = conn.cursor()
		cursor.execute("SELECT imgdata, name, caption, fname, lname FROM Users, Photos, Tags, Tagged WHERE Tags.tag_id = Tagged.tag_id AND Tagged.photo_id = Photos.photo_id AND Photos.user_id = Users.user_id AND Tags.name = '{0}'".format(tag))
		photos = cursor.fetchall()

		return render_template('photo_by_tags.html', message="Here are the photos for this tag.", photos = photos, base64=base64)
	else:
		return render_template('popular_tags.html', tags = TopTags())

def TopTags():
	cursor = conn.cursor()
	cursor.execute("SELECT name, COUNT(name) FROM Tags, Tagged WHERE Tags.tag_id = Tagged.tag_id GROUP BY name ORDER BY COUNT(name) DESC LIMIT 3")
	tags = cursor.fetchall()
	return tags

# Comments Methods
@app.route('/comment', methods=['GET', 'POST'])
def comment():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		photo_user_id = request.form.get('user_id')
		photo_user_id = int(photo_user_id)
		if uid == photo_user_id :
			return render_template('show_photos.html', message = "You cannot comment on your own photo!", photos = getUsersPhotos(uid), base64=base64)
		else:
			photo_id = request.form.get('photo_id')
			comment = request.form.get('comment')
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Comments (photo_id, user_id, text) VALUES ('{0}', '{1}', '{2}')".format(photo_id, uid, comment))
			conn.commit()
			return render_template('show_photos.html', message = "Comment added!", photos = getUsersPhotos(photo_user_id), base64=base64)

	return render_template('show_photos.html')

def getComment(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT text, fname, lname FROM Comments, Users WHERE Comments.user_id = Users.user_id AND Comments.photo_id = '{0}'".format(photo_id))
	comments = cursor.fetchall()
	return comments

@app.route('/search_comment', methods=['GET', 'POST'])
def SearchComments():
	if request.method == 'POST':
		comment = request.form.get('comment')
		cursor = conn.cursor()
		cursor.execute("SELECT fname, lname, COUNT(*) AS num_matches FROM Users, Comments WHERE Users.user_id = Comments.user_id AND text = '{0}' GROUP BY Users.user_id ORDER BY num_matches DESC".format(comment))
		comments = cursor.fetchall()

		return render_template('search_comment.html', message="Here are the users that commented this.", comments = comments)
	else:
		return render_template('search_comment.html')

# Likes Methods
@app.route('/like', methods=['GET', 'POST'])
@flask_login.login_required
def likePhoto():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		photo_id = request.form.get('photo_id')
		photo_id = int(photo_id)
		cursor = conn.cursor()
		cursor.execute("SELECT photo_id FROM Likes WHERE photo_id = '{0}' AND user_id = '{1}'".format(photo_id, uid))
		data = cursor.fetchall()

		for i in range(len(data)):
			if data[i][0] == photo_id:
				return render_template('show_photos.html', message = "You already liked this photo!", photos = getUsersPhotos(uid), base64=base64)


		cursor.execute("INSERT INTO Likes (photo_id, user_id) VALUES ('{0}', '{1}')".format(photo_id, uid))
		conn.commit()
		return render_template('show_photos.html', message = "Photo Liked!", photos = getUsersPhotos(uid), base64=base64)

	return render_template('show_photos.html', message="Here are your photos.", photos = getUsersPhotos(uid), base64=base64)

@app.route('/view_likes', methods=['GET', 'POST'])
def viewLikes():
	if request.method == 'POST':
		uid = request.form.get('user_id')
		photo_id = request.form.get('photo_id')
		likes = getLikes(photo_id)
		users = getWhoLiked(photo_id)
		return render_template('show_likes.html', message = "Here are the likes for this photo and who liked it.", likes = likes, users = users, photos = getUsersPhotos(uid), base64=base64)
	else:
		return render_template('show_likes.html')
	
def getLikes(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(user_id) FROM Likes WHERE photo_id = '{0}'".format(photo_id))
	likes = cursor.fetchall()
	return likes

def getWhoLiked(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT fname, lname FROM Likes, Users WHERE Likes.user_id = Users.user_id AND Likes.photo_id = '{0}'".format(photo_id))
	user = cursor.fetchall()
	return user

#user activity

@app.route('/top_users', methods=['GET'])
def showScore():
	cursor = conn.cursor()
	cursor.execute("SELECT fname, lname, SUM(num_pics) AS total_sum FROM (SELECT user_id, COUNT(photo_id) AS num_pics FROM Photos GROUP BY user_id UNION SELECT user_id, COUNT(comment_id) AS num_pics FROM Comments GROUP BY user_id) AS t1, Users WHERE t1.user_id = Users.user_id GROUP BY t1.user_id ORDER BY total_sum DESC LIMIT 10")
	score = cursor.fetchall()
	return render_template('top_users.html', message = "Here are the top 10 users who have contributed the most.", score = score)

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)