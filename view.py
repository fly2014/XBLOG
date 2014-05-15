# -*- coding: utf-8 -*-
import os
import cgi
import urllib
import jinja2
import webapp2
import comm
import json

from datetime import timedelta,datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.db import Model as DBModel
from google.appengine.api import datastore
from model import Tb_blog,Tb_tag,Tb_img,Tb_Blob,Tb_msg,Tb_link,Tb_config
from config import *
from cache import *
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

DEFAULT_GUESTBOOK_NAME='default_guestbook'

JINJA_ENVIRONMENT=jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)
import my_filters
JINJA_ENVIRONMENT.filters['gettimeba']=my_filters.gettimeba
JINJA_ENVIRONMENT.filters['gettimebad']=my_filters.gettimebad
JINJA_ENVIRONMENT.filters['gettime_date']=my_filters.gettime_date
JINJA_ENVIRONMENT.filters['get_titlecss']=my_filters.get_titlecss
JINJA_ENVIRONMENT.filters['get_pagecss']=my_filters.get_pagecss
JINJA_ENVIRONMENT.filters['get_blogstart']=my_filters.get_blogstart
JINJA_ENVIRONMENT.filters['commentpages']=my_filters.commentpages
JINJA_ENVIRONMENT.filters['getfontsize']=my_filters.getfontsize
JINJA_ENVIRONMENT.filters['smellimg']=comm.smellimg

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def obj_memcache_calendar_my(key):
	data = memcache.get(key.strftime('%Y-%m-%d-%H:%M:%S'))
	if (data==None):
		data=comm.calendar_my(key)
		memcache.set(key.strftime('%Y-%m-%d-%H:%M:%S'), data, 3600)
	return data

BASE=Tb_config.getp()
		
class BaseRequestHandler(webapp2.RequestHandler):
	def initialize(self, request, response):
		webapp2.RequestHandler.initialize(self, request, response)
		self.template_vals = {'COPYRIGHT':COPYRIGHT,'base':BASE,'nickname':users.get_current_user().nickname(),'current':'default','nickurl':users.create_logout_url('/')}
	def render2(self,template_file,template_vals={}):
		self.template_vals.update(template_vals)
		template=JINJA_ENVIRONMENT.get_template(template_file)
		self.response.write(template.render(self.template_vals))

class blog_BaseRequestHandler(webapp2.RequestHandler):
	def initialize(self, request, response):
		webapp2.RequestHandler.initialize(self, request, response)
		pagelist=Tb_blog.qypagetop(0)
		self.template_vals = {'COPYRIGHT':COPYRIGHT,'base':BASE,'pageurl':'/page/','pagelist':pagelist,'current':'default'}
	def render2(self,template_file,template_vals={},cdate=None):		
		self.template_vals.update(template_vals)
		if (cdate==None):
			cdate=datetime(comm.gettime().year,comm.gettime().month,1)
		self.template_vals['calendar_my']=obj_memcache_calendar_my(cdate)
		self.template_vals['r_link']=Tb_link.qyq()
		self.template_vals['r_blog']=Tb_blog.qyqc(BASE.BLOGCOUNT)
		self.template_vals['r_msg']=Tb_msg.qyqc(BASE.MSGCOUNT)
		self.template_vals['r_tag']=Tb_tag.qyqc(BASE.TAGCOUNT)		
		self.template_vals['r_class']=Tb_tag.qyclass()
		template=JINJA_ENVIRONMENT.get_template(template_file)
		self.response.write(template.render(self.template_vals))

class handle_404(blog_BaseRequestHandler):
	@request_memcache(key_prefix='handle404handler',time=3600*24)
	def get(self):
		template_values={'MKEY':'404,找不到您要的地址','SUBTITLE':'404 - 找不到您要的地址, 你可能输错了地址，或者你查看的东西已经不在了','Mtitle':'404 - 找不到您要的地址, 你可能输错了地址，或者你查看的东西已经不在了'}
		self.render2('template/404.html',template_values)

def handle_500(request, response, exception):
    response.write('500')
    response.set_status(500)

class mainindex(blog_BaseRequestHandler):
	@request_memcache(key_prefix='mainindexhandler',time=60*5)
	def get(self,pageindex=1):
		pagecount=BASE.BLOGCOUNTS
		pagecounty=pagecount%BASE.PAGENUMBER
		pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
		limit=(int(pageindex)-1)*BASE.PAGENUMBER
		template_values={'MKEY':BASE.MKEY,'SUBTITLE':BASE.MSUBTITLE,'Mtitle':BASE.MTITLE,'Bloglist':Tb_blog.qy_page_list(BASE.PAGENUMBER,limit),'pageindex':pageindex,'pagecount':pagecount}
		self.render2('template/index.html',template_values)
class main_page(blog_BaseRequestHandler):
	@request_memcache(key_prefix='mainpagehandler',time=60*5)
	def get(self,pagestr=None):
		if pagestr:
			pageindex=int(self.request.get('cpage','1'))
			blog=Tb_blog.getidpage(pagestr.decode("utf8"))
			blog.browse_count=blog.browse_count+1
			blog.put()
			blog_comment_list=blog.blog_comment_list(blog.key.id())		
			pagecount=blog_comment_list.count()
			pagecounty=pagecount%BASE.COMMENTNUMBER
			pagecount= pagecount/BASE.COMMENTNUMBER if pagecounty==0 else pagecount/BASE.COMMENTNUMBER+1
			limit=(int(pageindex)-1)*BASE.COMMENTNUMBER
			
			comment_author_=str(comm.urldecode(self.request.cookies.get('comment_author_', '')))
			comment_author_email_=comm.urldecode(self.request.cookies.get('comment_author_email_', ''))
			comment_author_url_=comm.urldecode(self.request.cookies.get('comment_author_url_', ''))
			
			template_values={'MKEY':blog.tagslistd,'SUBTITLE':blog.forewordd,'Mtitle':blog.titleb,'current':blog.pagename,'comment_author':comment_author_,'comment_author_email':comment_author_email_,'comment_author_url':comment_author_url_,'pagenumber':BASE.COMMENTNUMBER,'pageindex':pageindex,'pagecount':pagecount,'blog':blog,'comments':blog_comment_list.fetch(BASE.COMMENTNUMBER,offset=limit)}
			self.render2('template/page.html',template_values)
		else:
			self.redirect('/')

class show_blog(blog_BaseRequestHandler):
	def get(self,id=0):
		pageindex=int(self.request.get('cpage','1'))
		blog=Tb_blog.getidp(int(id))
		blog.browse_count=blog.browse_count+1
		blog.put()
		blog_comment_list=blog.blog_comment_list(blog.key.id())		
		pagecount=blog_comment_list.count()
		pagecounty=pagecount%BASE.COMMENTNUMBER
		pagecount= pagecount/BASE.COMMENTNUMBER if pagecounty==0 else pagecount/BASE.COMMENTNUMBER+1
		limit=(int(pageindex)-1)*BASE.COMMENTNUMBER
		
		comment_author_=str(comm.urldecode(self.request.cookies.get('comment_author_', '')))
		comment_author_email_=comm.urldecode(self.request.cookies.get('comment_author_email_', ''))
		comment_author_url_=comm.urldecode(self.request.cookies.get('comment_author_url_', ''))
		
		template_values={'MKEY':blog.tagslistd,'SUBTITLE':blog.forewordd,'Mtitle':blog.titleb,'comment_author':comment_author_,'comment_author_email':comment_author_email_,'comment_author_url':comment_author_url_,'pagenumber':BASE.COMMENTNUMBER,'pageindex':pageindex,'pagecount':pagecount,'blog':blog,'comments':blog_comment_list.fetch(BASE.COMMENTNUMBER,offset=limit)}
		self.render2('template/blog.html',template_values)

class main_s(blog_BaseRequestHandler):
	def get(self,str_key=None,pageindex=1):
		if str_key:
			querylist=Tb_blog.query(Tb_blog.title.IN(comm.china_Separate(str_key.decode("utf8"))))
			pagecount=querylist.count()
			pagecounty=pagecount%BASE.PAGENUMBER
			pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
			limit=(int(pageindex)-1)*BASE.PAGENUMBER
			mtitle=str_key
			template_values={'MKEY':str_key,'SUBTITLE':mtitle,'Mtitle':mtitle,'pageurl':'/s/'+str_key+'/','Bloglist':querylist.fetch(BASE.PAGENUMBER,offset=limit),'pageindex':pageindex,'pagecount':pagecount}
			self.render2('template/index.html',template_values)
		else:
			self.redirect('/')		

class main_tag(blog_BaseRequestHandler):
	def get(self,str_key=None,pageindex=1):
		if str_key:
			querylist=Tb_blog.query(Tb_blog.tags.IN([str_key.decode("utf8")]))
			pagecount=querylist.count()
			pagecounty=pagecount%BASE.PAGENUMBER
			pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
			limit=(int(pageindex)-1)*BASE.PAGENUMBER
			mtitle=str_key+'下的所有文章'
			template_values={'MKEY':str_key,'SUBTITLE':mtitle,'Mtitle':mtitle,'pageurl':'/tag/'+str_key+'/','Bloglist':querylist.fetch(BASE.PAGENUMBER,offset=limit),'pageindex':pageindex,'pagecount':pagecount}
			self.render2('template/index.html',template_values)
		else:
			self.redirect('/')

class main_category(blog_BaseRequestHandler):
	def get(self,classname=None,pageindex=1):
		if classname:
			tg=Tb_tag.getidclassname(classname.decode("utf8"))		
			querylist=Tb_blog.qyq(Tb_blog.classid==tg.key.id())
			pagecount=querylist.count()
			pagecounty=pagecount%BASE.PAGENUMBER
			pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
			limit=(int(pageindex)-1)*BASE.PAGENUMBER
			mtitle=tg.content+'下的所有文章'
			template_values={'MKEY':tg.content,'SUBTITLE':mtitle,'Mtitle':mtitle,'pageurl':'/category/'+classname+'/','Bloglist':querylist.fetch(BASE.PAGENUMBER,offset=limit),'pageindex':pageindex,'pagecount':pagecount}
			self.render2('template/index.html',template_values)
		else:
			self.redirect('/')
class praise_post(webapp2.RequestHandler):
	def get(self):
		self.response.write('请别乱搞!')
	def post(self):
		blog=Tb_blog.getidp(int(self.request.get('id','1')))
		blog.praise_count=blog.praise_count+1
		blog.put()
		self.response.write('/')
class comments_posts(webapp2.RequestHandler):
	def get(self):
		self.response.write('请别乱搞!')
	def post(self):
		edit_id=int(self.request.get('edit_id','0'))
		error=''
		errorstart=0
		if (edit_id>0):
			tb=Tb_msg.getidp(edit_id)
		else:
			tb=Tb_msg.init()
		email=self.request.get('email')
		nikname=self.request.get('author')
		content=self.request.get('comment')
		content=comm.filtermsg(content)
		blog_id=self.request.get('comment_post_ID')
		if (email):			
			if comm.validateEmail(email):
				tb.email=email
			else:
				error='Error：Email格式不正确！'
				errorstart=1
		else:
			error='Error：请输入Email！'
			errorstart=1
		if (nikname):
			tb.nikname=nikname
		else:
			error='Error：请输入昵称！'
			errorstart=1
		if (content):			
			if (comm.ischina(content)):
				tb.content=content
			else:
				error='Error：内容字数必须大于7小于300,且表情不能超过10个！'
				errorstart=1
		else:
			error='Error：请输入内容！'
			errorstart=1
		if (blog_id):
			tb.blog_id = int(blog_id)
		else:
			error='Error：请别乱搞！'
			errorstart=1
		if (errorstart>0):
			self.error(405)
			self.response.write(error)			
		else:
			tb.top_id=int(self.request.get('comment_parent','0'))
			tb.linkurl=self.request.get('url')
			tb.date = comm.gettime()
			tb.put()
			tbg=Tb_blog.getidp(tb.blog_id)
			tbg.comment_count=tbg.comment_count+1
			tbg.put()
			if (tb.top_id>0 and BASE.ISSENDMSG):
				addemail=Tb_msg.getidp(tb.top_id).email
				comm.sendemail('亲:'+addemail+','+tb.email+' 回复了你的留言,查看:'+BASE.HOSTURL+'/html/'+blog_id+'.html',BASE.EMAIL,addemail)
			template_values={'comment':tb,'base':BASE}
			template=JINJA_ENVIRONMENT.get_template('template/comment_return.html')
			
			comment_author_='comment_author_=%s;expires=%s;domain=%s;path=/'%( comm.urlencode(tb.nikname),(datetime.now()+timedelta(days=100)).strftime("%a, %d-%b-%Y %H:%M:%S GMT"),'' )
			self.response.headers.add_header( 'Set-Cookie', comment_author_)
			
			comment_author_email_='comment_author_email_=%s;expires=%s;domain=%s;path=/'%( comm.urlencode(tb.email),(datetime.now()+timedelta(days=100)).strftime("%a, %d-%b-%Y %H:%M:%S GMT"),'' )
			self.response.headers.add_header( 'Set-Cookie', comment_author_email_)
			
			comment_author_url_='comment_author_url_=%s;expires=%s;domain=%s;path=/'%( comm.urlencode(tb.linkurl),(datetime.now()+timedelta(days=100)).strftime("%a, %d-%b-%Y %H:%M:%S GMT"),'' )
			self.response.headers.add_header( 'Set-Cookie', comment_author_url_)
			
			self.response.write(template.render(template_values))
class sitemap(webapp2.RequestHandler):
	@request_memcache(key_prefix='sitemaphandler',time=3600*24)
	def get(self):
		Bloglist = Tb_blog.qyq(Tb_blog.ispage==False)
		template_vals={'entries':Bloglist,'base':BASE,'nowdate':comm.gettime()}
		self.response.headers['Content-Type'] = 'application/xml'
		template=JINJA_ENVIRONMENT.get_template('template/sitemap.xml')
		self.response.write(template.render(template_vals))
class feed(webapp2.RequestHandler):
	@request_memcache(key_prefix='commentsfeedhandler',time=3600*8)
	def get(self):
		Bloglist = Tb_blog.qyq(Tb_blog.ispage==False)
		template_vals={'entries':Bloglist,'base':BASE}
		self.response.headers['Content-Type'] = 'application/rss+xml'
		template=JINJA_ENVIRONMENT.get_template('template/rss.xml')
		self.response.write(template.render(template_vals))

class show_date(blog_BaseRequestHandler):	
	def get(self,y,m,d=None):
		if d:
			ondate=datetime(int(y),int(m),int(d))
			nextdate=comm.gettimeaddday(ondate,1)
			mtitle=ondate.strftime("%Y年%m月%d日的文章")
		else:
			ondate=datetime(int(y),int(m),1)
			nextdate=comm.add_months(ondate,1)
			mtitle=ondate.strftime("%Y年%m月的文章")
		
		querylist=Tb_blog.qyq(Tb_blog.ispage==False).filter(Tb_blog.date>ondate).filter(Tb_blog.date<nextdate).order(-Tb_blog.date)
		template_values={'MKEY':mtitle,'SUBTITLE':mtitle,'Mtitle':mtitle,'current':'img','Bloglist':querylist,'pageindex':1,'pagecount':1}
		self.render2('template/index.html',template_values,datetime(int(y),int(m),1))

class show_img(webapp2.RequestHandler):
	def get(self,id,fname):
		id=int(id)
		tb=Tb_img.getidp(id)
		#tbimg=Tb_Blob.getidp(tb.img_id)
		self.response.headers['Expires'] = 'Thu, 15 Apr 3010 20:00:00 GMT'
		self.response.headers['Cache-Control'] = 'max-age=3600,public'
		self.response.headers['Content-Type'] = str(tb.mtype)
		if (EXTS.count(str(tb.mext))==0):
			self.response.headers['Content-Disposition']='attachment; filename="' + str(tb.title)+'.'+ str(tb.mext) + '";'
		self.response.write(tb.bimg)

#管理员的
class ajax_img_list(webapp2.RequestHandler):
	def get(self,pageindex=1):
		pp=Tb_img.qyq()
		self.response.write(json.dumps([p.to_dict() for p in pp],cls=comm.ComplexEncoder,encoding='utf-8',ensure_ascii=False))
		#self.response.write(json.dumps(sample,cls=comm.ComplexEncoder,encoding='utf-8',ensure_ascii=False))
		#self.response.write(json.dumps([p.to_dict() for p in pp]))
class admin_default(BaseRequestHandler):
	def get(self):
		template_values={'current':'default'}
		self.render2('template/admin/index.html',template_values)

class public_delete(BaseRequestHandler):
	def get(self):
		tb=self.request.get('tb')
		id=self.request.get('id')
		if (tb=='blog'):
			Tb_blog.deletep(int(id))
			self.redirect('/admin/blog')
			return
		if (tb=='tag'):
			Tb_tag.deletep(int(id))
			self.redirect('/admin/tag')
			return
		if (tb=='img'):
			tb=Tb_img.getidp(int(id))
			Tb_Blob.deletep(tb.img_id)
			Tb_img.deletep(int(id))
			self.redirect('/admin/img')
			return
		if (tb=='link'):
			Tb_link.deletep(int(id))
			self.redirect('/admin/link')
			return
		if (tb=='comment'):
			if (len(id.split(','))>1):
				for ids in id.split(','):
					Tb_msg.deletep(int(ids))
				self.response.write('')
			else:
				Tb_msg.deletep(int(id))
				self.redirect('/admin/comment')
				return
		
class blog(BaseRequestHandler):
	def get(self,pageindex=1):
		#querylist=Tb_blog.qyq(Tb_blog.ispage==False)
		pagecount=int(BASE.BLOGCOUNTS)
		pagecounty=pagecount%BASE.PAGENUMBER
		pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
		limit=(int(pageindex)-1)*BASE.PAGENUMBER
		template_values={'issearch':True,'current':'blog','Blog':Tb_blog.qy_page_list(BASE.PAGENUMBER,limit),'pageindex':pageindex,'pagecount':pagecount}
		self.render2('template/admin/blog.html',template_values)

class blog_p(BaseRequestHandler):
	def get(self):
		template_values={'current':'blog','issearch':False,'Blog':Tb_blog.qypage()}
		self.render2('template/admin/blog.html',template_values)
def update_tag(tags):
	for tag in tags:
		tagentity=Tb_tag.getidtagname(tag)
		if tagentity:
			tagentity.mcount=tagentity.mcount+1
			tagentity.put()
		else:
			tb=Tb_tag.init()
			tb.content=tag
			tb.img_id=''
			tb.mcount =1
			tb.isclass = False
			tb.classname=''
			tb.classindex=0
			tb.date = comm.gettime()
			tb.put()
		
class blog_update_add(BaseRequestHandler):
	def get(self):
		Tags=Tb_tag.qyclass()
		pagelist=Tb_blog.qyq(Tb_blog.ispage==True)
		template_values={'current':'blog','action_url':self.request.path_qs,'Tags':Tags,'pagelist':pagelist}
		id=int(self.request.get('id','0'))		
		if (id>0):
			template_values.update({'blog':Tb_blog.getidp(id)})
			self.render2('template/admin/blog_update.html',template_values)
		else:
			self.render2('template/admin/blog_add.html',template_values)
	def post(self):
		id=int(self.request.get('id','0'))
		if (id>0):			
			tb=Tb_blog.getidp(id)
			tb.email=users.get_current_user().email()
			tb.title=comm.china_Separate(self.request.get('tb_title'))
			tb.titleb=self.request.get('tb_title')
			tb.foreword = self.request.get('tb_foreword')
			tb.content = self.request.get('tb_content')
			tb.tags=self.request.get('tb_tags').split(' ')
			#update_tag(tb.tags)
			tb.classid=int(self.request.get('tb_classid'))
			tb.top_id=int(self.request.get('tb_top_id'))
			tb.start=bool(self.request.get('tb_start'))
			tb.ispage=bool(self.request.get('tb_ispage'))
			tb.istop=bool(self.request.get('tb_istop'))
			tb.ismsg=bool(self.request.get('tb_ismsg'))
			tb.pagename=self.request.get('tb_pagename')
			pageindex=self.request.get("tb_pageindex")
			tb.pageindex=int(pageindex) if pageindex!='' else 0
			#tb.date = comm.gettime()
			tb.put()
		else:
			tb=Tb_blog.init()
			tb.browse_count =0
			tb.comment_count =0
			tb.praise_count=0
			tb.email=users.get_current_user().email()
			tb.title=comm.china_Separate(self.request.get('tb_title'))
			tb.titleb=self.request.get('tb_title')
			tb.foreword = self.request.get('tb_foreword')
			tb.content = self.request.get('tb_content')
			tb.tags=self.request.get('tb_tags').split(' ')
			update_tag(tb.tags)
			tb.classid=int(self.request.get('tb_classid'))
			tb.top_id=int(self.request.get('tb_top_id'))
			tb.start=bool(self.request.get('tb_start'))
			tb.ispage=bool(self.request.get('tb_ispage'))
			tb.istop=bool(self.request.get('tb_istop'))
			tb.ismsg=bool(self.request.get('tb_ismsg'))
			tb.pagename=self.request.get('tb_pagename')
			pageindex=self.request.get("tb_pageindex")
			tb.pageindex=int(pageindex) if pageindex!='' else 0
			tb.date = comm.gettime()
			tb.put()
		self.redirect('/admin/blog')

class Index(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:			
			if users.is_current_user_admin():
				self.redirect('/admin/')
			else:
				self.response.write('Welcome, %s! (<a href="%s">非管理员 退出重新登录</a>)' % (user.nickname(), users.create_logout_url('/admin')))
		else:
			self.response.write('<a href="%s">登录</a>' % users.create_login_url('/admin'))
			
class tag(BaseRequestHandler):
	def get(self,pageindex=1):
		querylist=Tb_tag.qyq()
		pagecount=querylist.count()
		pagecounty=pagecount%BASE.PAGENUMBER
		pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
		limit=(int(pageindex)-1)*BASE.PAGENUMBER
		template_values={'current':'tag','issearch':True,'Tag':querylist.fetch(BASE.PAGENUMBER,offset=limit),'pageindex':pageindex,'pagecount':pagecount}
		self.render2('template/admin/tag.html',template_values)
class tag_c(BaseRequestHandler):
	def get(self):
		template_values={'current':'tag','issearch':False,'Tag':Tb_tag.qyclass()}
		self.render2('template/admin/tag.html',template_values)

class tag_update_add(BaseRequestHandler):
	def get(self):
		template_values={'current':'tag','action_url':self.request.path_qs}
		id=int(self.request.get('id','0'))
		if (id>0):
			template_values.update({'tag':Tb_tag.getidp(id)})
			self.render2('template/admin/tag_update.html',template_values)
		else:
			self.render2('template/admin/tag_add.html',template_values)
	def post(self):
		id=int(self.request.get('id','0'))
		if (id>0):			
			tb=Tb_tag.getidp(id)
			tb.content=self.request.get('tb_content')
			tb.img_id=self.request.get('tb_img')
			tb.isclass = bool(self.request.get('tb_isclass'))
			tb.classname=self.request.get('tb_classname')
			classindex=self.request.get("tb_classindex")
			tb.classindex=int(classindex) if classindex!='' else 0
			tb.put()
		else:
			tb=Tb_tag.init()
			tb.content=self.request.get('tb_content')
			tb.img_id=self.request.get('tb_img')
			tb.mcount =0
			tb.isclass = bool(self.request.get('tb_isclass'))
			tb.classname=self.request.get('tb_classname')
			classindex=self.request.get("tb_classindex")
			tb.classindex=int(classindex) if classindex!='' else 0
			tb.date = comm.gettime()
			tb.put()
		self.redirect('/admin/tag')

class img(BaseRequestHandler):
	def get(self,pageindex=1):
		querylist=Tb_img.qyq()
		pagecount=querylist.count()
		pagecounty=pagecount%BASE.PAGENUMBER
		pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
		limit=(int(pageindex)-1)*BASE.PAGENUMBER
		template_values={'current':'img','Img':querylist.fetch(BASE.PAGENUMBER,offset=limit),'pageindex':pageindex,'pagecount':pagecount}
		self.render2('template/admin/img.html',template_values)
	
class img_update_add(BaseRequestHandler):
	def get(self):
		template_values={'current':'img','action_url':self.request.path_qs}
		id=int(self.request.get('id','0'))
		if (id>0):
			template_values.update({'img':Tb_img.getidp(id)})
			self.render2('template/admin/img_update.html',template_values)
		else:
			self.render2('template/admin/img_add.html',template_values)
	def post(self):
		id=int(self.request.get('id','0'))
		if (id>0):			
			tb=Tb_img.getidp(id)
			tbimg=Tb_Blob.getidp(tb.img_id)
			tb.title=self.request.get('tb_title')
			tb.mtype=self.request.get('tb_mtype')
			tb.mext=self.request.get('tb_mext')
			
			tbimg.img =self.request.get('tb_img')
			width=int(self.request.get('tb_width'))
			height=int(self.request.get('tb_height'))
			if (width>0):
				img = images.Image(tbimg.img)
				img.resize(width=width, height=height)
				img.im_feeling_lucky()
				tbimg.img = img.execute_transforms(output_encoding=images.JPEG)
			tbimg.put()			
			tb.put()
		else:
			tb=Tb_img.init()
			tbimg=Tb_Blob.init()
			tb.title=self.request.get('tb_title')
			tbimg.img =self.request.get('tb_img')
			width=int(self.request.get('tb_width'))
			height=int(self.request.get('tb_height'))
			if (width>0):
				img = images.Image(tbimg.img)
				img.resize(width=width, height=height)
				img.im_feeling_lucky()
				tbimg.img = img.execute_transforms(output_encoding=images.JPEG)
			tbimg.put()
			tb.img_id =tbimg.key.id()
			tb.mtype=self.request.get('tb_mtype')
			tb.mext=self.request.get('tb_mext')
			tb.date = comm.gettime()
			tb.put()
		self.redirect('/admin/img')

class msg_list(BaseRequestHandler):
	def get(self,pageindex=1):
		querylist=Tb_msg.qyq()
		pagecount=querylist.count()
		pagecounty=pagecount%BASE.PAGENUMBER
		pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
		limit=(int(pageindex)-1)*BASE.PAGENUMBER
		template_values={'current':'comment','msgs':querylist.fetch(BASE.PAGENUMBER,offset=limit),'pageindex':pageindex,'pagecount':pagecount}
		self.render2('template/admin/msg.html',template_values)

class link(BaseRequestHandler):
	def get(self,pageindex=1):
		querylist=Tb_link.qyq()
		pagecount=querylist.count()
		pagecounty=pagecount%BASE.PAGENUMBER
		pagecount= pagecount/BASE.PAGENUMBER if pagecounty==0 else pagecount/BASE.PAGENUMBER+1
		limit=(int(pageindex)-1)*BASE.PAGENUMBER
		template_values={'current':'link','links':querylist.fetch(BASE.PAGENUMBER,offset=limit),'pageindex':pageindex,'pagecount':pagecount}
		self.render2('template/admin/link.html',template_values)

class link_update_add(BaseRequestHandler):
	def get(self):
		template_values={'current':'link','action_url':self.request.path_qs}
		id=int(self.request.get('id','0'))
		if (id>0):
			template_values.update({'link':Tb_link.getidp(id)})
			self.render2('template/admin/link_update.html',template_values)
		else:
			self.render2('template/admin/link_add.html',template_values)
	def post(self):
		id=int(self.request.get('id','0'))
		if (id>0):			
			tb=Tb_link.getidp(id)
			tb.title=self.request.get('tb_title')
			tb.link=self.request.get('tb_link')	
			tb.put()
		else:
			tb=Tb_link.init()
			tb.title=self.request.get('tb_title')
			tb.link=self.request.get('tb_link')		
			tb.date = comm.gettime()
			tb.put()
		self.redirect('/admin/link')

class config(BaseRequestHandler):
	def get(self):
		template_values={'current':'config','action_url':self.request.path_qs}
		self.render2('template/admin/config.html',template_values)
	def post(self):
		tb=Tb_config.getp()
		tb.AUTHOR=self.request.get('AUTHOR')
		tb.EMAIL=self.request.get('EMAIL')
		tb.HOSTURL=self.request.get('HOSTURL')
		tb.TITLE=self.request.get('TITLE')
		tb.SUBTITLE=self.request.get('SUBTITLE')
		tb.KEY=self.request.get('KEY')
		tb.MTITLE=self.request.get('MTITLE')
		tb.MSUBTITLE=self.request.get('MSUBTITLE')
		tb.MKEY=self.request.get('MKEY')
		tb.PAGENUMBER=int(self.request.get('PAGENUMBER'))
		tb.COMMENTNUMBER=int(self.request.get('COMMENTNUMBER'))
		tb.ISHEADEG=bool(int(self.request.get('ISHEADEG')))
		tb.ISSENDMSG=bool(int(self.request.get('ISSENDMSG')))
		tb.CLASSBLOGCOUNT=int(self.request.get('CLASSBLOGCOUNT'))
		tb.TAGCOUNT=int(self.request.get('TAGCOUNT'))
		tb.BLOGCOUNT=int(self.request.get('BLOGCOUNT'))
		tb.MSGCOUNT=int(self.request.get('MSGCOUNT'))
		tb.Prompt=self.request.get('Prompt')
		tb.Announcement=self.request.get('Announcement')
		tb.BLOGCOUNTS=Tb_blog.qyq(Tb_blog.ispage==False).count()
		tb.QQ=self.request.get('QQ')
		tb.Qweibo=self.request.get('Qweibo')
		tb.Sweibo=self.request.get('Sweibo')
		tb.TONGJI=self.request.get('TONGJI')
		tb.date = comm.gettime()
		tb.put()
		global BASE
		BASE=Tb_config.getp()
		#memcache.flush_all()
		ObjCache.flush_all()
		self.redirect('/admin/config')