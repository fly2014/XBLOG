# -*- coding: utf-8 -*-
from datetime import timedelta,datetime
import json
import re
import urllib
import urllib2
import calendar

from model import Tb_blog
from config import * 
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import users

def gettime():
	t=datetime.now()+timedelta(hours=+8)
	return t
def gettimeaddday(t,d):
	t=t+timedelta(days=+d)
	return t
def china_Separate(v):
	#return list(v)
	url = 'http://www.xunsearch.com/scws/api.php'
	values = {'data':v,'respond':'json'}
	data = urllib.urlencode(values)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	the_page = response.read()
	wordjson = json.loads(the_page)
	if (wordjson['status']=='ok'):
		jvlist=[]
		for jlist in wordjson['words']:
			jvlist.append(jlist['word'])
		return jvlist
	else:
		return list(v)
class ComplexEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		elif isinstance(obj, datetime.date):
			return obj.strftime('%Y-%m-%d')
		else:
			return json.JSONEncoder.default(self, obj)
def validateEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return True
	return False
def sendemail(body,semail,to_addr):
	message = mail.EmailMessage()
	message.sender = semail
	message.to = to_addr
	message.body =body
	message.send()
def ischina(v):
	if (len(v) > 7) and (len(v) < 301):
		if(len(v.split(':'))<22):
			return True
	return False
imagelist=[{'href':':mrgreen:','image':'icon_mrgreen.gif'},
	{'href':':razz:','image':'icon_razz.gif'},
	{'href':':sad:','image':'icon_sad.gif'},
	{'href':':smile:','image':'icon_smile.gif'},
	{'href':':oops:','image':'icon_redface.gif'},
	{'href':':grin:','image':'icon_biggrin.gif'},
	{'href':':eek:','image':'icon_surprised.gif'},
	{'href':':???:','image':'icon_confused.gif'},
	{'href':':cool:','image':'icon_cool.gif'},
	{'href':':lol:','image':'icon_lol.gif'},
	{'href':':mad:','image':'icon_mad.gif'},
	{'href':':twisted:','image':'icon_twisted.gif'},
	{'href':':roll:','image':'icon_rolleyes.gif'},
	{'href':':wink:','image':'icon_wink.gif'},
	{'href':':idea:','image':'icon_idea.gif'},
	{'href':':arrow:','image':'icon_arrow.gif'},
	{'href':':neutral:','image':'icon_neutral.gif'},
	{'href':':cry:','image':'icon_cry.gif'},
	{'href':':?:','image':'icon_question.gif'},
	{'href':':evil:','image':'icon_evil.gif'},
	{'href':':shock:','image':'icon_eek.gif'},
	{'href':':!:','image':'icon_exclaim.gif'}]

def smellimg(v,t=0):
	if (t==0):
		for item in imagelist:	
			v=v.replace(item['href'],'<img src="/style/bluesky/images/smilies/%s">' % item['image'])
		return v
	else:
		return '<script>document.write(msgreplace(\''+v+'\'))</script>'
def filtermsg(v):
	scontent=str(v).decode('utf-8')
	scontent=scontent.replace('\r\n',' ')
	scontent=re.sub(r'<br\s*/>',' ',scontent)
	scontent=re.sub(r'<[^>]+>','',scontent)
	scontent=re.sub(r'(@[\S]+)-\d{2,7}',r'\1:',scontent)
	return scontent.replace('<','&lt;').replace('>','&gt;')
def urlencode(value):
	return urllib.quote(value.encode("utf8"))
def urldecode(value):
	return  urllib.unquote(str(value)).decode('utf-8')

cn_month={'1':'一','2':'二','3':'三','4':'四','5':'五','6':'六','7':'七','8':'八','9':'九','10':'十','11':'十一','12':'十二',}
def add_months(dt,months):
	month = dt.month - 1 + months
	year = dt.year + month / 12
	month = month % 12 + 1
	day = min(dt.day,calendar.monthrange(year,month)[1])
	return dt.replace(year=year, month=month, day=day)
def dayOfMonth(date):
	return int(calendar.monthrange(date.year,date.month)[1])
def istoday_idcss(date,iday):
	noedate=gettime()
	if (noedate.day==iday and date.month==noedate.month and date.year==noedate.year):
		return ' id="today" '
	else:
		return ''
def day_isa(listday,iday,ym):
	if (listday.count(iday)==1):
		return '<a href="/'+ym+'-'+str(iday)+'" title="浏览">'+str(iday)+'</a>'
	else:
		return str(iday)
def calendar_my(datevalue):
	datevalue=add_months(datevalue,1)
		
	query_blog_list=Tb_blog.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(Tb_blog.ispage==False).filter(Tb_blog.date<datevalue).order(-Tb_blog.date).fetch(1,projection=[Tb_blog.date])

	for blog in query_blog_list:
		datevalue=blog.date
		break
	
	ondate=datetime(datevalue.year,datevalue.month,1)
	nextdate=add_months(ondate,1)
	query_blog_list=Tb_blog.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(Tb_blog.ispage==False).filter(Tb_blog.date>ondate).filter(Tb_blog.date<nextdate).order(Tb_blog.date).fetch(projection=[Tb_blog.date])
	daylist=[]
	for blog in query_blog_list:
		if (daylist.count(blog.date.day)==1):
			continue
		else:
			daylist.append(blog.date.day)
			
	wekday=int(ondate.strftime("%w"))
	monthcount=dayOfMonth(ondate)
	wekdayl=int(datetime(ondate.year,ondate.month,monthcount).strftime("%w"))
	
	onquery_blog_list=Tb_blog.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(Tb_blog.ispage==False).filter(Tb_blog.date<ondate).order(-Tb_blog.date).fetch(1,projection=[Tb_blog.date])
	nextquery_blog_list=Tb_blog.query(ancestor=Gxcmd_key(PARENT_NAME)).filter(Tb_blog.ispage==False).filter(Tb_blog.date>nextdate).order(Tb_blog.date).fetch(1,projection=[Tb_blog.date])
	
	onstr=''
	nextstr=''
	for blog in onquery_blog_list:
		onstr='<a href="/%s" title="查看%s年%s月的文章">« %s</a>' % (blog.date.strftime('%Y-%m'),str(blog.date.year),cn_month[str(blog.date.month)],cn_month[str(blog.date.month)])

	for blog in nextquery_blog_list:
		nextstr='<a href="/%s" title="查看%s年%s月的文章">%s »</a>' % (blog.date.strftime('%Y-%m'),str(blog.date.year),cn_month[str(blog.date.month)],cn_month[str(blog.date.month)])
	
	calendar_str1='''<div id="calendar-1" class="widget sidebar-box widget_calendar"><div id="calendar_wrap"><table id="wp-calendar"><caption>%s年%s月</caption>
		<thead><tr><th scope="col" title="星期一">一</th><th scope="col" title="星期二">二</th><th scope="col" title="星期三">三</th><th scope="col" title="星期四">四</th><th scope="col" title="星期五">五</th><th scope="col" title="星期六">六</th><th scope="col" title="星期日">日</th></tr></thead>
		<tfoot>
		<tr>
			<td colspan="3" id="prev">%s</td>
			<td class="pad">&nbsp;</td>
			<td colspan="3" id="next">%s</td>
		</tr></tfoot><tbody>'''
	calendar_str2='<tr>'
	if (wekday==0):
		wekday=7
	if (wekday-1>0):
		calendar_str2=calendar_str2+'<td colspan="'+str(wekday-1)+'" class="pad">&nbsp;</td>'
	indexday=1
	
	while (indexday<=monthcount):
		if (wekday==7):
			calendar_str2=calendar_str2+'<td'+istoday_idcss(ondate,indexday)+'>'+day_isa(daylist,indexday,datevalue.strftime("%Y-%m"))+'</td></tr><tr>'
			wekday=1
			indexday+=1
		else:
			calendar_str2=calendar_str2+'<td'+istoday_idcss(ondate,indexday)+'>'+day_isa(daylist,indexday,datevalue.strftime("%Y-%m"))+'</td>'
			indexday+=1
			wekday+=1
	if (wekdayl==0):
		lastc=len(calendar_str2)-4
		calendar_str2=calendar_str2[0:lastc]
	else:
		calendar_str2=calendar_str2+'<td colspan="'+str(7-wekdayl)+'" class="pad">&nbsp;</td></tr>'
	calendar_str3='''</tbody></table></div></div>'''
	return (calendar_str1+calendar_str2+calendar_str3) % (datevalue.year,cn_month[str(datevalue.month)],onstr,nextstr)