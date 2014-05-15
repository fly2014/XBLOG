$(function(){
	if($.browser.msie){
		$(".author_show, .uface").hover(function(){
			var d=$(this).find(".author_detail");
			d.show().css("z-index",1337).css("opacity",1);
		},function(){
			var d=$(this).find(".author_detail");
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
	}
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
		var site='http://www.example.com/';
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
		jQuery('#sina-share').click(function(){
			var url='http://v.t.sina.com.cn/share/share.php?url='+link+'&title='+title;
			var params=getParamsOfShareWindow(607,523);
			window.open(url,windowName,params);
		});
		jQuery('#tencent-share').click(function(){
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
});