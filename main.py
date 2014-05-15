#-*-coding:utf-8-*-
import os
import cgi
import urllib
import jinja2
import webapp2

from datetime import timedelta,datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.db import Model as DBModel
from google.appengine.api import datastore

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import view		
app=webapp2.WSGIApplication([
	('/',view.mainindex),
	('/page/(\d+)',view.mainindex),
	('/page/(.*).html',view.main_page),
	('/tag/(.*)/(\d+)',view.main_tag),
	('/tag/(.*)',view.main_tag),	
	('/s/(.*)/(\d+)',view.main_s),
	('/s/(.*)',view.main_s),
	('/category/(.*)/(\d+)',view.main_category),
	('/category/(.*)',view.main_category),	
	('/(\d{4})-(\d{2})',view.show_date),
	('/(\d{4})-(\d{2})-(\d+)',view.show_date),
	('/html/(.*).html',view.show_blog),
	('/comments_posts',view.comments_posts),
	('/img/(.*)/(.*)',view.show_img),
	('/admin',view.Index),
	('/praise_post',view.praise_post),
	('/feed',view.feed),
	('/sitemap.xml',view.sitemap),
	('.*',view.handle_404)
],debug=True)
#app.error_handlers[500] = view.handle_500
#app.error_handlers[404] = view.handle_404