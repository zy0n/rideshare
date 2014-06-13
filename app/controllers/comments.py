import json
from google.appengine.ext import db
from app.model import *
import datetime
from app.base_handler import BaseHandler
from app.common import voluptuous

def get_key(id, type):
	key = ''
	if type == 'ride':
		ride = Ride.get_by_id(id)
		key = ride.key()
	elif type == 'event':
		event = Event.get_by_id(id)
		key = event.key()
	elif type == 'circle':
		circle = Circle.get_by_id(id)
		key = circle.key()
	elif type == 'profile':
		user = User.get_by_id(id)
		key = user.key()
	return key

class CommentHandler(BaseHandler):
	def post(self):
		self.auth()

		user = self.current_user()

		json_str = self.request.body
		data = json.loads(json_str)

		d = datetime.date.today()

		comment = Comment()
		comment.user = user.key()
		comment.date = d
		comment.text = data['comment']
		if data['type'] == 'ride':
			ride = Ride.get_by_id(data['id'])
			comment.ride = ride.key()
		elif data['type'] == 'event':
			event = Event.get_by_id(data['id'])
			comment.event = event.key()
		elif data['type'] == 'circle':
			circle = Circle.get_by_id(data['id'])
			comment.circle = circle.key()
		elif data['type'] == 'profile':
			user = User.get_by_id(data['id'])
			comment.profile = user.key()
		comment.put()

		self.response.write(json.dumps({
			'message': 'Success',
			'name': user.name,
			'date': str(d),
			'comment': comment.text,
			'id': comment.key().id()
		}))

class FetchComments(BaseHandler):
	def post(self):
		self.auth()

		user = self.current_user()

		json_str = self.request.body
		data = json.loads(json_str)

		key = get_key(data['id'], data['type'])

		comments = Comment.all().filter(data['type'] + " = ", key).order('-date').fetch(25)



		resp = [c.to_dict() for c in comments]

		for res in resp:
			if res['user']['id'] == user.key().id():
				res['is_owner'] = True
			else:
				res['is_owner'] = False

		self.response.write(json.dumps(resp))

class GetComment(BaseHandler):
	def get(self, comment_id):
		self.auth()

		comment = Comment.get_by_id(int(comment_id))

		doRender(self, 'edit_comment.html', {
			'comment': comment
		})