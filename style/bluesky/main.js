$(function(){
	/*if($.browser.msie){
		$(".uface").hover(function(){
			var d=$(".author_detail");
			d.show().css("z-index",1337).css("opacity",1);
		},function(){
			var d=$(".author_detail");
			d.hide().css("z-index",-1337);
		})
	}else{
		$(".author_show, .uface").hover(function(){
			var d=$(this).find(".author_detail");
			d.show().css("z-index",1337).animate({opacity:1},100)
		},function(){
			var d=$(this).find(".author_detail");
			d.animate({opacity:0},100,
			function(){
				$(this).hide().css("z-index",-1337)
			})
		})
	}*/
	$("span.views").click(function(){
		var vspan=$(this);
		$.post("/praise_post",{id:vspan.attr('v')},function(data) {
			vspan.html(1+parseInt(vspan.html()));
		});
	});
	$(".share-tumblr").each(function(){var d=$(this).attr("href").replace("url=http://","url=");$(this).attr("href",d)});
	$(document).click(function() {
		$('#sharebar').hide();
	});
	$('span.zh_share span').click(function(event) {
		event.stopPropagation();
	});
	$('span.zh_share span').each(function(){
		$(this).click(function(){
			$(this).next().toggle();
		})
	});

	function getParamsOfShareWindow(width,height){
		return['toolbar=0,status=0,resizable=1,width='+width+',height='+height+',left=',(screen.width-width)/2,',top=',(screen.height-height)/2].join('');
	}
	function bindShareList(){
		var link=encodeURIComponent(document.location);
		var title=encodeURIComponent(document.title.substring(0,76));
		var source=encodeURIComponent('网站名称');
		var windowName='share';
		var site='http://blog.xcmd.net/';
		jQuery('#twitter-share').click(function(){
			var url='http://twitter.com/share?url='+link+'&text='+title;
			var params=getParamsOfShareWindow(500,375);
			window.open(url,windowName,params);
		});
		jQuery('#kaixin001-share').click(function(){
			var url='http://www.kaixin001.com/repaste/share.php?rurl='+link+'&rcontent='+link+'&rtitle='+title;
			var params=getParamsOfShareWindow(540,342);
			window.open(url,windowName,params);
		});
		jQuery('#renren-share').click(function(){
			var url='http://share.renren.com/share/buttonshare?link='+link+'&title='+title;
			var params=getParamsOfShareWindow(626,436);
			window.open(url,windowName,params);
		});
		jQuery('#douban-share').click(function(){
			var url='http://www.douban.com/recommend/?url='+link+'&title='+title;
			var params=getParamsOfShareWindow(450,350);
			window.open(url,windowName,params);
		});
		jQuery('#fanfou-share').click(function(){
			var url='http://fanfou.com/sharer?u='+link+'?t='+title;
			var params=getParamsOfShareWindow(600,400);
			window.open(url,windowName,params);
		});
		jQuery('.sina-share').click(function(){
			var url='http://v.t.sina.com.cn/share/share.php?url='+link+'&title='+title;
			var params=getParamsOfShareWindow(607,523);
			window.open(url,windowName,params);
		});
		jQuery('.tencent-share').click(function(){
			var url='http://v.t.qq.com/share/share.php?title='+title+'&url='+link+'&site='+site;
			var params=getParamsOfShareWindow(634,668);
			window.open(url,windowName,params);
		});
	}
	bindShareList();
	
	//回到顶部的JS
	var back_top_btn = $('#back_top');
	if(back_top_btn.length) {
		$(window).scroll(function () {
			setTimeout(function() {
				var scrollTop = $(this).scrollTop();
				if (scrollTop > 400) {
					back_top_btn.fadeIn();
				} else {
					back_top_btn.fadeOut();
				}
			},64);
		});
		back_top_btn.on('click',function (e) {
			e.preventDefault();
			$('body,html').animate({scrollTop: 0}, 400);
		});
	}
	$('#searchsubmit').click(function() {
		window.location.href='/s/'+$('#s').val();
		return false;
	});
});
/**
* 字符串格式化，类似于java中的MessageFormat.format() 函数
* e.g.
* 'This is a {0} not a {1}.'.format('string', 'num') =&gt; This is a string not a num.
* 'This is a {0}, not a {1}. so parse to {2} first.'.format('string', 'num', 'num') =&gt; This is a string not a num. so parse to num first.
* 'This is a {0}, not a {1}. so parse to {1} first.'.format('string', 'num') =&gt; This is a string not a num. so parse to num first.
* 'This is a {0}, not a {1}. so parse to {2} first.'.format('string', 'num') =&gt; This is a string not a num. so parse to {2} first.
*/
String.prototype.format = function() {
	var args = arguments;
	return this.replace(/\{(\d+)\}/g, function(){
		var val = args[arguments[1]];
		alert(val + '  ' + arguments[0]);
		return (! val) ? arguments[0] : val;
	});
};
function msgreplace(str)
{
var path='<img src="/style/bluesky/images/smilies/{0}.gif">'
str=str.replaceall(':mrgreen:',path.format('icon_mrgreen'));
str=str.replaceall(':razz:',path.format('icon_razz'));
str=str.replaceall(':sad:',path.format('icon_sad'));
str=str.replaceall(':smile:',path.format('icon_smile'));
str=str.replaceall(':oops:',path.format('icon_redface'));
str=str.replaceall(':grin:',path.format('icon_biggrin'));
str=str.replaceall(':eek:',path.format('icon_surprised'));
str=str.replaceall(':???:',path.format('icon_confused'));
str=str.replaceall(':cool:',path.format('icon_cool'));
str=str.replaceall(':lol:',path.format('icon_lol'));
str=str.replaceall(':mad:',path.format('icon_mad'));
str=str.replaceall(':twisted:',path.format('icon_twisted'));
str=str.replaceall(':roll:',path.format('icon_rolleyes')); 
str=str.replaceall(':wink:',path.format('icon_wink')); 
str=str.replaceall(':idea:',path.format('icon_idea'));
str=str.replaceall(':arrow:',path.format('icon_arrow'));
str=str.replaceall(':neutral:',path.format('icon_neutral'));
str=str.replaceall(':cry:',path.format('icon_cry')); 
str=str.replaceall(':?:',path.format('icon_question')); 
str=str.replaceall(':evil:',path.format('icon_evil'));
str=str.replaceall(':shock:',path.format('icon_eek')); 
str=str.replaceall(':!:',path.format('icon_exclaim'));
return str;
}