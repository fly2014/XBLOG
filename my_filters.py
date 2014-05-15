# -*- coding: utf-8 -*-
from datetime import timedelta,datetime

def gettimeba(v):
	return v.strftime("%Y-%m-%d %H:%M:%S")
def gettimebad(v):
	return v.strftime("%Y.%m.%d")
def gettime_date(v):
	return v.strftime("%Y-%m-%d")
def get_titlecss(v,k):
	if (v==k):
		return 'class=current'
	else:
		return ''
def get_pagecss(v,k):
	if (v==k):
		return 'current_page_item'
	else:
		return ''	
def get_blogstart(v):
	if (v):
		return '发布'
	else:
		return '草稿'
def getfontsize(v):
	v=v+6
	if (v>20):
		return 22
	else:
		return v	
	
def commentpages(pageindex,pagenumber,ispage,pagename,bid):
	if ispage:
		blog_id=str(pagename)
		htmltype='page'
	else:
		blog_id=str(bid)
		htmltype='html'
	
	if (pagenumber==0):
		return ''
	if (pageindex-1==0):
		page1=''
	else:
		page1='<a class="prev page-numbers" href="/'+htmltype+'/'+str(blog_id)+'.html?cpage='+str(pageindex-1)+'#comments">«</a>'
	if (pageindex==pagenumber):
		page3=''
	else:
		page3='<a class="next page-numbers" href="/'+htmltype+'/'+str(blog_id)+'.html?cpage='+str(pageindex+1)+'#comments">»</a>'	
	index=1
	page=''
	while (index<=pagenumber):
		if (index==pageindex):
			page=page+'<span class="page-numbers current">'+str(index)+'</span>'
		else:
			page=page+'<a class="page-numbers" href="/'+htmltype+'/'+str(blog_id)+'.html?cpage='+str(index)+'#comments">'+str(index)+'</a>'
		index=index+1
	return '<div class="comment_page_navi">'+page1+page+page3+'</div>'