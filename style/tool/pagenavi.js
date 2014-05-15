function showPageLink(sUrl,iPage,iCount,sAnchor){
    var i;
    i=Math.max(1,iPage-1);
    if(iPage==1){
        document.write("<a class='pdisable'>首页</a> ");
        document.write("<a class='pdisable'>上一页</a> ");
    }
    else{
        document.write("<a href=\"" + sUrl + sAnchor + "1\" title='第 1 页'>首页</a> ");
        document.write("<a href=\"" + sUrl + i + sAnchor + "\" title='上一页(第 " + i + " 页)'>上一页</a> ");
    }
    if(iPage>6) document.write("<span>...</span> ");
    for(i=Math.max(1,iPage-5);i<iPage;i++){
        document.write("<a href=\""+sUrl + i + sAnchor + "\" title='第 " + i + " 页'><b>" + i + "</b></a> ");
    }
    document.write("<a  class='acurr'>" + iPage + "</a> ");
    for(i=iPage+1;i<=Math.min(iCount,iPage+5);i++){
        document.write("<a href=\""+sUrl + i + sAnchor + "\" title='第 " + i + " 页'><b>" + i + "</b></a> ");
    }
    i=Math.min(iCount,iPage+1);
    if(iCount>iPage+5) document.write("<span>...</span> ");
    if(iPage==iCount||iCount==0){
        document.write("<a class='pdisable'>下一页</a> ");
        document.write("<a class='pdisable'>尾页</a> ");
    }
    else{
        document.write("<a href=\"" + sUrl + i + sAnchor + "\" title='下一页(第 " + i + " 页)'>下一页</a> ");
        document.write("<a href=\"" + sUrl + iCount + sAnchor + "\" title='最后一页(第 " + iCount + " 页)'>尾页</a> ");
    }
}

