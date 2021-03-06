# -*- coding: utf-8 -*-
###################################################
#this file is under GPL v3 license
#Author: Rex  fdrex1987@gmail.com
#the code of format_date is from Micolog's code
##################################################
import logging
import pickle
from google.appengine.ext import db
from google.appengine.api import memcache
from datetime import datetime

class ObjCache(db.Model):
	cache_key = db.StringProperty()
	value = db.BlobProperty()
	datetime = db.DateTimeProperty(auto_now=True)
	tags = db.StringListProperty()
#	is_htmlpage = db.BooleanProperty(default=False) #即request所缓存的那种 TODO:invalidate some cache when posting an article
#	comment_type = db.StringProperty(default='') #'ALL','NORMAL'
#	is_basicinfo = db.BooleanProperty(default=False)
#	is_count = db.BooleanProperty(default=False)
#	is_aggregation = db.BooleanProperty(default=False)
#	is_pager = db.BooleanProperty(default=False)
#	entry_id = db.IntegerProperty(default=-1)#post_id
#   is_hotposts

	def invalidate(self):
		logging.debug('ObjCache invalidate called: ' + self.cache_key)
		memcache.delete(self.cache_key)
		self.delete()

	def update(self, new_value_obj):
		logging.debug('ObjCache update called: ' + self.cache_key)
		memcache.set(self.cache_key,new_value_obj)
		self.value = pickle.dumps(new_value_obj)
		self.put()

	@staticmethod
	def get_cache_value(key_name):
		result = memcache.get(key_name)
		if result is not None:
			logging.debug("Find cache value of "+key_name+" in memcache.")
			return result
		try:
			result = ObjCache.all().filter('cache_key =',key_name).get()
			if result is not None:
				logging.debug("Find cache value of "+key_name+" in ObjCache.")
				return pickle.loads(result.value)
			else:
				return None
		except Exception, e:
			logging.error(e.message)
			return None

	@staticmethod
	def update_basic_info(
		update_categories=False,
		update_tags=False,
		update_links=False,
		update_comments=False,
		update_archives=False,
		update_pages=False):

		from model import Entry,Archive,Comment,Category,Tag,Link
		basic_info = ObjCache.get(is_basicinfo=True)
		if basic_info is not None:
			info = ObjCache.get_cache_value(basic_info.cache_key)
			if update_pages:
				info['menu_pages'] = Entry.all().filter('entrytype =','page')\
							.filter('published =',True)\
							.filter('entry_parent =',0)\
							.order('menu_order').fetch(limit=1000)
			if update_archives:
				info['archives'] = Archive.all().order('-year').order('-month').fetch(12)
			if update_comments:
				info['recent_comments'] = Comment.all().order('-date').fetch(5)
			if update_links:
				info['blogroll'] = Link.all().filter('linktype =','blogroll').fetch(limit=1000)
			if update_tags:
				info['alltags'] = Tag.all().order('-tagcount').fetch(limit=100)
			if update_categories:
				info['categories'] = Category.all().fetch(limit=1000)

			logging.debug('basic_info updated')
			basic_info.update(info)

	@staticmethod
	def create(key, value_obj, is_htmlpage=None,comment_type=None,is_basicinfo=None,
	           is_count=None,is_aggregation=None,is_pager=None,entry_id=None,is_hotposts=None):
		try:
			memcache.set(key,value_obj)
			l = []
			if is_htmlpage is not None:
				l.append(u'is_htmlpage='+unicode(is_htmlpage))
			if comment_type is not None:
				l.append(u'comment_type='+unicode(comment_type))
			if is_basicinfo is not None:
				l.append(u'is_basicinfo='+unicode(is_basicinfo))
			if is_count is not None:
				l.append(u'is_count='+unicode(is_count))
			if is_aggregation is not None:
				l.append(u'is_aggregation='+unicode(is_aggregation))
			if is_pager is not None:
				l.append(u'is_pager='+unicode(is_pager))
			if entry_id is not None:
				l.append(u'entry_id='+unicode(entry_id))
			if is_hotposts is not None:
				l.append(u'is_hotposts='+unicode(is_hotposts))

			#logging.debug('kwargs: '+str(kwargs))
			ObjCache(cache_key=key,value=pickle.dumps(value_obj), tags=l).put()
			logging.debug("ObjCache created with key: " + key + " and with tags: " + unicode(l))
		except Exception:
			logging.exception('Exception in cache.create.')

	@staticmethod
	def flush_multi(**kwargs):
		logging.debug('ObjCache.flush_multi called with parameters: '+unicode(kwargs))
		flush = ObjCache.all()
		for key in kwargs:
			flush = flush.filter('tags =',key+'='+unicode(kwargs[key]))
		for obj in flush:
			obj.invalidate()

	@staticmethod
	def filter(**kwargs):
		logging.debug('ObjCache.filter with parameters: '+unicode(kwargs))
		result = ObjCache.all()
		for key in kwargs:
			result = result.filter('tags =',key+'='+unicode(kwargs[key]))
		return result

	@staticmethod
	def get(**kwargs):
		logging.debug('ObjCache.get with parameters: '+unicode(kwargs))
		result = ObjCache.all()
		for key in kwargs:
			result = result.filter('tags =',key+'='+unicode(kwargs[key]))
		result = result.get()
		if result:
			logging.debug('ObjCache.get result: ' + unicode(result.cache_key))
		return result

	@classmethod
	def flush_all(cls):
		'''
		This is faster than invalidate with default parameter values since memcache only need one call
		'''
		logging.debug('ObjCache flush all called')
		memcache.flush_all()
		i=0
		try:
			for cache in ObjCache.all():
				i = i+1
				cache.delete()
			logging.debug('ObjCache.flush_all: '+unicode(i)+" items flushed")
		except Exception:
			logging.exception('Exception in ObjCache.flush_all')
			logging.debug('ObjCache.flush_all: '+unicode(i)+" items flushed")

def object_cache(key_prefix='',
                 key_parameter_name='cache_key',
                 cache_parameter_prefix='cache_',
                 cache_control_parameter_name='cache_control',
                 **other_kwargs):
	'''
	available options for cache control are: no_cache, cache
	default option is cache
	'''
	def _decorate(method):
		def _wrapper(*args, **kwargs):
			key = 'obj_'+key_prefix
			if key_parameter_name in kwargs:
				key = key+'_'+kwargs[key_parameter_name]
				del kwargs[key_parameter_name]

			cache_control = 'cache'
			if cache_control_parameter_name in kwargs:
				cache_control = kwargs[cache_control_parameter_name]
				del kwargs[cache_control_parameter_name]
				
			cache_args = other_kwargs
			to_add = {}
			for parameter_name in kwargs:
				if parameter_name.startswith(cache_parameter_prefix):
					cache_arg_name = parameter_name[len(cache_parameter_prefix):]
					to_add[cache_arg_name] = kwargs[parameter_name]
					
			for parameter in to_add:
				cache_args[parameter] = to_add[parameter]
				del kwargs[cache_parameter_prefix + parameter]

			if cache_control == 'no_cache':
				logging.debug('object_cache: no_cache for '+key)
				return method(*args, **kwargs)

			result = ObjCache.get_cache_value(key)
			if result is not None:
				logging.debug('object_cache: result found for '+key)
				return result

			logging.debug('object_cache: result not found for '+key)
			result = method(*args, **kwargs)
			ObjCache.create(key,result,**cache_args)
			return result

		return _wrapper
	return _decorate

def object_memcache(key_prefix='',time=3600,
                 key_parameter_name='cache_key',
                 cache_control_parameter_name='cache_control'):
	'''
	available options for cache control are: no_cache, cache
	default option is cache
	'''
	def _decorate(method):
		def _wrapper(*args, **kwargs):
			key = 'memcache_'+key_prefix
			if key_parameter_name in kwargs:
				key = key+'_'+kwargs[key_parameter_name]
				del kwargs[key_parameter_name]

			cache_control = 'cache'
			if cache_control_parameter_name in kwargs:
				cache_control = kwargs[cache_control_parameter_name]
				del kwargs[cache_control_parameter_name]

			if cache_control == 'no_cache':
				logging.debug('@@@**************************object_memcache: no_cache for '+key)
				return method(*args, **kwargs)

			result = memcache.get(key)
			if result is not None:
				logging.debug('@@@@***************************object_memcache: found key for '+key)
				return result

			logging.debug('@@@@@************************object_memcache: not found key for '+key)
			result = method(*args, **kwargs)
			memcache.set(key,result,time)
			return result
		return _wrapper
	return _decorate

@object_cache(key_prefix='get_query_count',is_count=True)
def get_query_count(query):
	if hasattr(query,'__len__'):
		return len(query)
	else:
		return query.count()

def format_date(dt):
	return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

def request_cache(key_prefix='',
                  key_parameter_name='cache_key',
                  cache_parameter_prefix='cache_',
                  cache_control_parameter_name='cache_control',
                  **other_kwargs):
	'''
	available options for cache control are: no_cache, cache
	default option is cache
	'''
	def _decorate(method):
		def _wrapper(*args, **kwargs):
			request=args[0].request
			response=args[0].response

			key = 'request_'+key_prefix+'_'+request.path_qs
			if key_parameter_name in kwargs:
				key = key+'_'+kwargs[key_parameter_name]
				del kwargs[key_parameter_name]

			cache_control = 'cache'
			if cache_control_parameter_name in kwargs:
				cache_control = kwargs[cache_control_parameter_name]
				del kwargs[cache_control_parameter_name]
				
			cache_args = other_kwargs
			cache_args['is_htmlpage'] = True
			to_add = {}
			for parameter_name in kwargs:
				if parameter_name.startswith(cache_parameter_prefix):
					cache_arg_name = parameter_name[len(cache_parameter_prefix):]
					to_add[cache_arg_name] = kwargs[parameter_name]
			for parameter in to_add:
				cache_args[parameter] = to_add[parameter]
				del kwargs[cache_parameter_prefix + parameter]

			if cache_control == 'no_cache':
				logging.debug('request_cache: no_cache for '+key)
				if 'last-modified' not in response.headers:
						response.last_modified = format_date(datetime.utcnow())
				method(*args, **kwargs)
				return

			html= ObjCache.get_cache_value(key)
			if html:
				logging.debug('request_cache: found cache for '+key)
				try:
					response.last_modified =html[1]
					_len=len(html)
					if _len>=3:
						response.set_status(html[2])
					if _len>=4:
						for h_key,value in html[3].items():
							response.headers[h_key]=value
					response.out.write(html[0])
					return
				except Exception,e:
					logging.error(e.message)

			logging.debug('request_cache: not found cache for '+key)
			if 'last-modified' not in response.headers:
				response.last_modified = format_date(datetime.utcnow())

			method(*args, **kwargs)
			result=response.out.getvalue()
			status_code = response._Response__status[0]
			html = (result,response.last_modified,status_code,response.headers)
			ObjCache.create(key,html,**cache_args)
			return

		return _wrapper
	return _decorate

def request_memcache(key_prefix='',time = 3600,
                  key_parameter_name='cache_key',
                  cache_control_parameter_name='cache_control'):
	'''
	available options for cache control are: no_cache, cache
	default option is cache
	'''
	def _decorate(method):
		def _wrapper(*args, **kwargs):
			request=args[0].request
			response=args[0].response
			
			key = 'request_'+key_prefix+'_'+request.path_qs
			if key_parameter_name in kwargs:
				key = key+'_'+kwargs[key_parameter_name]
				del kwargs[key_parameter_name]

			cache_control = 'cache'
			if cache_control_parameter_name in kwargs:
				cache_control = kwargs[cache_control_parameter_name]
				del kwargs[cache_control_parameter_name]

			if cache_control == 'no_cache':
				logging.debug('request_cache: no_cache for '+key)
				if 'last-modified' not in response.headers:
					response.last_modified = format_date(datetime.utcnow())
				method(*args, **kwargs)
				return

			html= ObjCache.get_cache_value(key)
			if html:
				logging.debug('request_cache: found cache for '+key)
				try:
					response.last_modified =html[1]
					_len=len(html)
					if _len>=3:
						response.set_status(html[2])
					if _len>=4:
						for h_key,value in html[3].items():
							response.headers[h_key]=value
					response.write(html[0])
					return
				except Exception,e:
					logging.error(e.message)

			logging.debug('request_cache: not found cache for '+key)
			if 'last-modified' not in response.headers:
				response.last_modified = format_date(datetime.utcnow())

			method(*args, **kwargs)
			#result=response.out.GetValue()
			result=response.body			
			status_code = response.status.split()[0]
			html = (result,response.last_modified,status_code,response.headers)
			memcache.set(key,html,time)
			return

		return _wrapper
	return _decorate
