# -*- coding: utf-8 -*-
import os
import cgi
import jinja2
import webapp2
from google.appengine.api import users
import view

		
app = webapp2.WSGIApplication([
	('/admin/', view.admin_default),
	('/admin/index', view.admin_default),
	('/admin/blog', view.blog),
	('/admin/blog/(\d+)', view.blog),
	('/admin/blog_p', view.blog_p),
	('/admin/blog_add', view.blog_update_add),
	('/admin/blog_uptata', view.blog_update_add),
	('/admin/blog_delete', view.public_delete),
	('/admin/tag', view.tag),
	('/admin/tag/(\d+)', view.tag),
	('/admin/tag_c', view.tag_c),
	('/admin/tag_uptata', view.tag_update_add),
	('/admin/tag_add', view.tag_update_add),
	('/admin/tag_delete', view.public_delete),
	('/admin/img', view.img),
	('/admin/img/(\d+)', view.img),
	('/admin/ajax_img_list', view.ajax_img_list),
	('/admin/img_add', view.img_update_add),
	('/admin/img_uptata', view.img_update_add),
	('/admin/img_delete', view.public_delete),
	('/admin/comment', view.msg_list),
	('/admin/comment/(\d+)', view.msg_list),
	('/admin/comment_delete', view.public_delete),
	('/admin/link', view.link),
	('/admin/link_uptata', view.link_update_add),
	('/admin/link_add', view.link_update_add),
	('/admin/link/(\d+)', view.link),
	('/admin/link_delete', view.public_delete),
	('/admin/config',view.config)
], debug=True)