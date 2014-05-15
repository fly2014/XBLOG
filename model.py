# -*- coding: utf-8 -*-
import os
import cgi
import jinja2
import webapp2
import urllib, hashlib,urlparse
import zipfile,re,pickle,uuid
from config import * 
from cache import *
import random

from datetime import timedelta, datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.db import Model as DBModel
from google.appengine.api import datastore

#基础设置
class Tb_base(ndb.Model):
	@classmethod
	def qyq(cls):
		query_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).order(-cls.date)
		return query_list
	@classmethod
	def qyqc(cls,count):
		query_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).order(-cls.date).fetch(count)
		return query_list	
	@classmethod
	def deletep(cls,kid):
		et=cls.get_by_id(kid,parent=Gxcmd_key(PARENT_NAME))
		if et:
			et.key.delete()
	@classmethod
	def delete(cls,kid):
		et=cls.get_by_id(kid)
		if et:
			et.key.delete()
	@classmethod	
	def init(cls):
		return cls(parent=Gxcmd_key(PARENT_NAME))
	@classmethod
	def getidp(cls,kid):
		return cls.get_by_id(kid,parent=Gxcmd_key(PARENT_NAME))
	@classmethod
	def getid(cls,kid):
		return cls.get_by_id(kid)

class Tb_img(Tb_base):
	title=ndb.StringProperty(indexed=False)
	img_id = ndb.IntegerProperty(indexed=False)
	mtype=ndb.StringProperty(indexed=False)
	mext=ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty()
	@property
	def bimg(self):
		return Tb_Blob.getidp(self.img_id).img

class Tb_Blob(Tb_base):
	img=ndb.BlobProperty(indexed=False)
class Tb_link(Tb_base):
	title=ndb.StringProperty(indexed=False)
	link=ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty()
#标签
class Tb_tag(Tb_base): 
	content = ndb.StringProperty(indexed=True)
	mcount=ndb.IntegerProperty(indexed=True)
	isclass=ndb.BooleanProperty()
	img_id = ndb.StringProperty(indexed=False)
	classname=ndb.StringProperty(indexed=True)
	classindex=ndb.IntegerProperty(indexed=True)
	date = ndb.DateTimeProperty()

	@classmethod
	def qyclass(cls):		
		return cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.isclass==True).order(cls.classindex)
	@classmethod
	def getidclassname(cls,classname):
		query_tag=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.classname==classname).get()
		return query_tag
	@classmethod
	def getidtagname(cls,content):
		query_tag=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.content==content).get()
		return query_tag
	@classmethod
	def qyqc(cls,m_count):
		query_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.mcount>1).fetch(m_count)
		return query_list
#内容
class Tb_blog(Tb_base): 
	email = ndb.StringProperty(indexed=False)
	title = ndb.StringProperty(repeated=True)
	titleb = ndb.StringProperty(indexed=False)
	foreword = ndb.StringProperty(indexed=False)
	content = ndb.StringProperty(indexed=False)
	tags=ndb.StringProperty(repeated=True)
	browse_count = ndb.IntegerProperty(indexed=True)
	comment_count = ndb.IntegerProperty(indexed=True)
	praise_count = ndb.IntegerProperty(indexed=True)
	classid = ndb.IntegerProperty(indexed=True)
	start=ndb.BooleanProperty()
	ispage=ndb.BooleanProperty()
	pagename=ndb.StringProperty(indexed=True)
	pageindex=ndb.IntegerProperty(indexed=True)
	top_id = ndb.IntegerProperty(indexed=True)
	istop=ndb.BooleanProperty()
	ismsg=ndb.BooleanProperty()
	date = ndb.DateTimeProperty()
	@classmethod
	def getidpage(cls,pagestr):
		query_blog=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.pagename==pagestr).get()
		return query_blog
	@classmethod
	def getidpagechard(cls,top_id):
		query_blog=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.top_id==top_id).order(cls.pageindex)
		return query_blog
	@classmethod
	def qyq(cls,t):
		query_blog=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(t).order(-cls.date)
		return query_blog
	@classmethod
	def qyqc(cls,m_count):
		query_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.ispage==False).order(-cls.date).fetch(m_count)
		return query_list
	@classmethod
	def qypage(cls):
		query_blog=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.ispage==True).order(cls.pageindex)
		return query_blog
	@classmethod
	def qypagetop(cls,tid):
		query_blog=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.ispage==True).filter(cls.top_id==tid).order(cls.pageindex)
		return query_blog
	@property
	def classimg(self):
		return Tb_tag.getidp(self.classid).img_id
	@property
	def classname(self):
		return Tb_tag.getidp(self.classid).classname
	@property
	def tagname(self):
		return Tb_tag.getidp(self.classid).content
	@property
	def tagslist(self):
		return ' '.join(self.tags)
	@property
	def tagslistd(self):
		return ','.join(self.tags)
	@property
	def titlelist(self):
		return ''.join(self.title)
	@classmethod
	def onpage(cls,kdate):
		query_onpage=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.date<kdate).filter(cls.ispage==False).order(-cls.date).fetch(1)
		return query_onpage
	@classmethod
	def nextpage(cls,kdate):
		query_nextpage=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.date>kdate).filter(cls.ispage==False).order(cls.date).fetch(1)
		return query_nextpage
	@classmethod
	def class_blog_list(cls,cid,CLASSBLOGCOUNT):
		query_blog_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.classid==cid).order(-cls.date).fetch(CLASSBLOGCOUNT)
		return query_blog_list
	@classmethod
	def blog_comment_list(cls,blog_id):
		query_comment_list=Tb_msg.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(Tb_msg.blog_id==blog_id).filter(Tb_msg.top_id==0).order(cls.date)
		return query_comment_list
	@classmethod
	def qy_page_list(cls,pagenumber,limit):
		query_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.ispage==False).order(-cls.date).fetch(pagenumber,offset=limit)
		return query_list
	@property
	def forewordd(self):
		scontent=str(self.foreword).decode('utf-8')
		scontent=re.sub(r'<br\s*/>',' ',scontent)
		scontent=re.sub(r'<[^>]+>','',scontent)
		scontent=re.sub(r'(@[\S]+)-\d{2,7}',r'\1:',scontent)
		return scontent.replace('<','&lt;').replace('>','&gt;').replace('\n',' ').strip()
#留言
class Tb_msg(Tb_base): 
	nikname = ndb.StringProperty(indexed=False)
	linkurl = ndb.StringProperty(indexed=False)
	top_id=ndb.IntegerProperty(indexed=True)
	email = ndb.StringProperty(indexed=False)
	blog_id = ndb.IntegerProperty(indexed=True)
	content = ndb.StringProperty(indexed=False)
	isshow=ndb.BooleanProperty(indexed=True)
	date = ndb.DateTimeProperty()
	@classmethod
	def children(cls,top_id):
		query_msg_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(cls.top_id==top_id).order(cls.date)
		return query_msg_list
	@property
	def shortcontent(self,len=30):
		scontent=str(self.content).decode('utf-8')
		scontent=re.sub(r'<br\s*/>',' ',scontent)
		scontent=re.sub(r'<[^>]+>','',scontent)
		scontent=re.sub(r'(@[\S]+)-\d{2,7}',r'\1:',scontent)
		return scontent[:len].replace('<','&lt;').replace('>','&gt;')
	@classmethod
	def gravatar_url(cls,email,ISHEADEG):
		if ISHEADEG:
			return '/style/img/touxiang/%s.png' % random.randint(1,9)			
		else:
			default='http://blog.xcmd.net/style/img/touxiang/default.jpg'
			if not email:
				return default
			size = 50
			default = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
			default += urllib.urlencode({'d':default, 's':str(size)})			
			return default

class Tb_config(Tb_base):
	AUTHOR=ndb.StringProperty(indexed=False)
	EMAIL=ndb.StringProperty(indexed=False)
	HOSTURL=ndb.StringProperty(indexed=False)
	TITLE=ndb.StringProperty(indexed=False)
	SUBTITLE=ndb.StringProperty(indexed=False)
	KEY=ndb.StringProperty(indexed=False)
	PAGENUMBER=ndb.IntegerProperty(indexed=False)
	COMMENTNUMBER=ndb.IntegerProperty(indexed=False)
	ISHEADEG=ndb.BooleanProperty(indexed=False)
	CLASSBLOGCOUNT=ndb.IntegerProperty(indexed=False)
	TAGCOUNT=ndb.IntegerProperty(indexed=False)
	BLOGCOUNT=ndb.IntegerProperty(indexed=False)
	MSGCOUNT=ndb.IntegerProperty(indexed=False)
	Prompt=ndb.StringProperty(indexed=False)
	Announcement=ndb.StringProperty(indexed=False)	
	BLOGCOUNTS=ndb.IntegerProperty(indexed=False)
	ISSENDMSG=ndb.BooleanProperty(indexed=False)
	QQ=ndb.StringProperty(indexed=False)
	Qweibo=ndb.StringProperty(indexed=False)
	Sweibo=ndb.StringProperty(indexed=False)
	TONGJI=ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty()
	MTITLE=ndb.StringProperty(indexed=False)
	MSUBTITLE=ndb.StringProperty(indexed=False)
	MKEY=ndb.StringProperty(indexed=False)
	@classmethod
	def getp(cls):
		query_list=cls.query(ancestor=Gxcmd_key(PARENT_NAME)).order(cls.date)
		if query_list:			
			for c in query_list:
				return c
			tb=Tb_config.init()
			tb.AUTHOR='Xblog1'
			tb.TITLE='Xblog'
			tb.SUBTITLE='Xblog'
			tb.KEY='Xblog'
			tb.MTITLE='Xblog'
			tb.MSUBTITLE='Xblog'
			tb.MKEY='Xblog'
			tb.PAGENUMBER=5
			tb.COMMENTNUMBER=5
			tb.ISHEADEG=False
			tb.CLASSBLOGCOUNT=5
			tb.TAGCOUNT=5
			tb.BLOGCOUNT=5
			tb.MSGCOUNT=5
			tb.Prompt=''
			tb.Announcement=''
			tb.BLOGCOUNTS=5
			tb.ISSENDMSG=True
			tb.QQ='848109696'
			tb.Qweibo=''
			tb.Sweibo=''
			tb.TONGJI='© 2007-2013 XBLOG All rights reserved. 中ICP备2014007号'
			tb.put()
			return tb
		else:
			tb=Tb_config.init()
			tb.AUTHOR='Xblog1'
			tb.TITLE='Xblog'
			tb.SUBTITLE='Xblog'
			tb.KEY='Xblog'
			tb.MTITLE='Xblog'
			tb.MSUBTITLE='Xblog'
			tb.MKEY='Xblog'
			tb.PAGENUMBER=5
			tb.COMMENTNUMBER=5
			tb.ISHEADEG=False
			tb.CLASSBLOGCOUNT=5
			tb.TAGCOUNT=5
			tb.BLOGCOUNT=5
			tb.MSGCOUNT=5
			tb.Prompt=''
			tb.Announcement=''
			tb.BLOGCOUNTS=5
			tb.ISSENDMSG=True
			tb.QQ='848109696'
			tb.Qweibo=''
			tb.Sweibo=''
			tb.TONGJI='© 2007-2013 XBLOG All rights reserved. 中ICP备2014007号'
			tb.put()
			return tb