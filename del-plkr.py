#!/usr/bin/env python
# Heavily based on http://notes.natbat.net/2007/03/06/delicioussnaflr/
import urllib2, urllib, time, datetime
from xml.dom import minidom

deliciousUsername = 'xxxx'
deliciousPassword = 'xxxx'

tag = 'plkr'

class DeliciousAccount():
	apiRoot = 'https://api.del.icio.us/'

	def __init__(self, username, password):
		"""Logs into delicious"""

		pmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		pmgr.add_password(
			None, self.apiRoot, username, password
		)
		auth_handler = urllib2.HTTPBasicAuthHandler(pmgr)
		self.opener = urllib2.build_opener(auth_handler)

	def get_response_root(self, uri, rootTag):
		response = minidom.parseString(self.opener.open(uri).read())
		return response.getElementsByTagName(rootTag)[0]

	def get_update_time(self):
		"""retrieve last update time"""
		update = self.get_response_root(self.apiRoot+'v1/posts/update', 'update')
		return update.getAttribute('time')

	def get_posts(self, tag=None):
		"""Retrieve posts, filtered by optional tag"""
		uri = self.apiRoot+'v1/posts/all?'
		if tag is not None:
			uri += 'tag=%s'%tag
		pList = self.get_response_root(uri, 'posts').getElementsByTagName('post')
		return [ DeliciousPost(p) for p in pList ]

	def update_post(self, post):
		result = self.get_response_root(
				self.apiRoot+'v1/posts/add?'+post.Info,
				'result')
		return result.getAttribute('code')

def urlencode(d):
	for key, value in d.items():
		if isinstance(value, unicode):
			d[key] = value.encode('utf-8')
	return urllib.urlencode(d)

class DeliciousPost():
	def __init__(self, xmlPost):
		self.url = xmlPost.getAttribute('href')
		self.description = xmlPost.getAttribute('description')
		self.extended = xmlPost.getAttribute('extended')
		self.tags = xmlPost.getAttribute('tag').split()
		self.time = xmlPost.getAttribute('time')
		# privacy flag?  need to see what it is called

	def Info(self):
		return urlencode({
			'url': self.url,
			'description': self.description,
			'extended': self.extended,
			'tags': " ".join(self.tags),
			'dt': self.time,
			'replace': 'yes'
		})


def syncronise_account():
	"""Kickstarts the whole kaboodle"""
	print 'starting sync' 
	delAcct = DeliciousAccount(deliciousUsername, deliciousPassword)
	print delAcct.get_update_time()
	posts = delAcct.get_posts(tag)

	for p in posts:
		print "Processing ", p.url, " ...",
		p.tags.remove(tag)
		print delAcct.update_post(p)
		time.sleep(2)


if __name__ == '__main__':
	syncronise_account()
