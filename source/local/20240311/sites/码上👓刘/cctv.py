#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import base64
import re
from urllib import request, parse
import urllib
import urllib.request
import time

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "中央电视台"#可搜索
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电视剧": "电视剧",
			"动画片": "动画片",
			"纪录片": "纪录片",
			"特别节目": "特别节目",
            "栏目大全": "栏目大全"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		result = {
			'list':[]
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		month = ""#月
		year = ""#年
		area=''#地区
		channel=''#频道
		datafl=''#类型
		letter=''#字母
		pagecount=24
		if tid=='动画片':
			id=urllib.parse.quote(tid)
			if 'datadq-area' in extend.keys():
				area=urllib.parse.quote(extend['datadq-area'])
			if 'dataszm-letter' in extend.keys():
				letter=extend['dataszm-letter']
			if 'datafl-sc' in extend.keys():
				datafl=urllib.parse.quote(extend['datafl-sc'])
			url='https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955899450127&area={0}&sc={4}&fc={1}&letter={2}&p={3}&n=24&serviceId=tvcctv&topv=1&t=json'.format(area,id,letter,pg,datafl)
		elif tid=='纪录片':
			id=urllib.parse.quote(tid)
			if 'datapd-channel' in extend.keys():
				channel=urllib.parse.quote(extend['datapd-channel'])
			if 'datafl-sc' in extend.keys():
				datafl=urllib.parse.quote(extend['datafl-sc'])
			if 'datanf-year' in extend.keys():
				year=extend['datanf-year']
			if 'dataszm-letter' in extend.keys():
				letter=extend['dataszm-letter']
			url='https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955924871139&fc={0}&channel={1}&sc={2}&year={3}&letter={4}&p={5}&n=24&serviceId=tvcctv&topv=1&t=json'.format(id,channel,datafl,year,letter,pg)
		elif tid=='电视剧':
			id=urllib.parse.quote(tid)
			if 'datafl-sc' in extend.keys():
				datafl=urllib.parse.quote(extend['datafl-sc'])
			if 'datanf-year' in extend.keys():
				year=extend['datanf-year']
			if 'dataszm-letter' in extend.keys():
				letter=extend['dataszm-letter']
			url='https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955853485115&area={0}&sc={1}&fc={2}&year={3}&letter={4}&p={5}&n=24&serviceId=tvcctv&topv=1&t=json'.format(area,datafl,id,year,letter,pg)
		elif tid=='特别节目':
			id=urllib.parse.quote(tid)
			if 'datapd-channel' in extend.keys():
				channel=urllib.parse.quote(extend['datapd-channel'])
			if 'datafl-sc' in extend.keys():
				datafl=urllib.parse.quote(extend['datafl-sc'])
			if 'dataszm-letter' in extend.keys():
				letter=extend['dataszm-letter']
			url='https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955953877151&channel={0}&sc={1}&fc={2}&bigday=&letter={3}&p={4}&n=24&serviceId=tvcctv&topv=1&t=json'.format(channel,datafl,id,letter,pg)
		elif tid=='栏目大全':
			cid=''#频道
			if 'cid' in extend.keys():
				cid=extend['cid']
			fc=''#分类
			if 'fc' in extend.keys():
				fc=extend['fc']
			fl=''#字母
			if 'fl' in extend.keys():
				fl=extend['fl']
			url = 'https://api.cntv.cn/lanmu/columnSearch?&fl={0}&fc={1}&cid={2}&p={3}&n=20&serviceId=tvcctv&t=json&cb=ko'.format(fl,fc,cid,pg)
			pagecount=20
		else:
			url = 'https://tv.cctv.com/epg/index.shtml'

		videos=[]
		htmlText =self.webReadFile(urlStr=url,header=self.header)
		if tid=='栏目大全':
			index=htmlText.rfind(');')
			if index>-1:
				htmlText=htmlText[3:index]
				videos =self.get_list1(html=htmlText,tid=tid)
		else:
			videos =self.get_list(html=htmlText,tid=tid)
		#print(videos)
		
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 9999 if len(videos)>=pagecount else pg
		result['limit'] = 90
		result['total'] = 999999
		return result
	def detailContent(self,array):
		result={}
		aid = array[0].split('###')
		tid = aid[0]
		logo = aid[3]
		lastVideo = aid[2]
		title = aid[1]
		id= aid[4]
		
		vod_year= aid[5]
		actors= aid[6]
		brief= aid[7]
		fromId='CCTV'
		if tid=="栏目大全":
			lastUrl = 'https://api.cntv.cn/video/videoinfoByGuid?guid={0}&serviceId=tvcctv'.format(id)
			htmlTxt = self.webReadFile(urlStr=lastUrl,header=self.header)
			topicId=json.loads(htmlTxt)['ctid']
			Url = "https://api.cntv.cn/NewVideo/getVideoListByColumn?id={0}&d=&p=1&n=100&sort=desc&mode=0&serviceId=tvcctv&t=json".format(topicId)
			htmlTxt = self.webReadFile(urlStr=Url,header=self.header)
		else:
			Url='https://api.cntv.cn/NewVideo/getVideoListByAlbumIdNew?id={0}&serviceId=tvcctv&p=1&n=100&mode=0&pub=1'.format(id)
		jRoot = ''
		videoList = []
		try:
			if tid=="搜索":
				fromId='中央台'
				videoList=[title+"$"+lastVideo]
			else:
				htmlTxt=self.webReadFile(urlStr=Url,header=self.header)
				jRoot = json.loads(htmlTxt)
				data=jRoot['data']
				jsonList=data['list']
				videoList=self.get_EpisodesList(jsonList=jsonList)
				if len(videoList)<1:
					htmlTxt=self.webReadFile(urlStr=lastVideo,header=self.header)
					if tid=="电视剧" or tid=="纪录片":
						patternTxt=r"'title':\s*'(?P<title>.+?)',\n{0,1}\s*'brief':\s*'(.+?)',\n{0,1}\s*'img':\s*'(.+?)',\n{0,1}\s*'url':\s*'(?P<url>.+?)'"
					elif tid=="特别节目":
						patternTxt=r'class="tp1"><a\s*href="(?P<url>https://.+?)"\s*target="_blank"\s*title="(?P<title>.+?)"></a></div>'
					elif tid=="动画片":
						patternTxt=r"'title':\s*'(?P<title>.+?)',\n{0,1}\s*'img':\s*'(.+?)',\n{0,1}\s*'brief':\s*'(.+?)',\n{0,1}\s*'url':\s*'(?P<url>.+?)'"
					elif tid=="栏目大全":
						patternTxt=r'href="(?P<url>.+?)" target="_blank" alt="(?P<title>.+?)" title=".+?">'
					videoList=self.get_EpisodesList_re(htmlTxt=htmlTxt,patternTxt=patternTxt)
					fromId='央视'
		except:
			pass
		if len(videoList) == 0:
			return {}
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":tid,
			"vod_year":vod_year,
			"vod_area":"",
			"vod_remarks":'',
			"vod_actor":actors,
			"vod_director":'',
			"vod_content":brief
		}
		vod['vod_play_from'] = fromId
		vod['vod_play_url'] = "#".join(videoList)
		result = {
			'list':[
				vod
			]
		}
		return result
	def get_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit	
	def get_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	def searchContent(self,key,quick):
		key=urllib.parse.quote(key)
		Url='https://search.cctv.com/ifsearch.php?page=1&qtext={0}&sort=relevance&pageSize=20&type=video&vtime=-1&datepid=1&channel=&pageflag=0&qtext_str={0}'.format(key)
		htmlTxt=self.webReadFile(urlStr=Url,header=self.header)
		videos=self.get_list_search(html=htmlTxt,tid='搜索')
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		url=''
		parse=0
		headers = {
			'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
		}
		if flag=='CCTV':
			url=self.get_m3u8(urlTxt=id)
		else:
			try:
				html=self.webReadFile(urlStr=id,header=self.header)
				guid=self.get_RegexGetText(Text=html,RegexText=r'var\sguid\s*=\s*"(.+?)";',Index=1)
				url=self.get_m3u8(urlTxt=guid)
			except :
				url=id
				parse=1
		if url.find('https:')<0:
			url=id
			parse=1
		result["parse"] = parse#1=嗅探,0=播放
		result["playUrl"] = ''
		result["url"] = url
		result["header"] =headers
		return result
	config = {
		"player": {},
		"filter": {
		"电视剧":[
		{"key":"datafl-sc","name":"类型","value":[{"n":"全部","v":""},{"n":"谍战","v":"谍战"},{"n":"悬疑","v":"悬疑"},{"n":"刑侦","v":"刑侦"},{"n":"历史","v":"历史"},{"n":"古装","v":"古装"},{"n":"武侠","v":"武侠"},{"n":"军旅","v":"军旅"},{"n":"战争","v":"战争"},{"n":"喜剧","v":"喜剧"},{"n":"青春","v":"青春"},{"n":"言情","v":"言情"},{"n":"偶像","v":"偶像"},{"n":"家庭","v":"家庭"},{"n":"年代","v":"年代"},{"n":"革命","v":"革命"},{"n":"农村","v":"农村"},{"n":"都市","v":"都市"},{"n":"其他","v":"其他"}]},
		{"key":"datanf-year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"},{"n":"1999","v":"1999"},{"n":"1998","v":"1998"},{"n":"1997","v":"1997"}]},
		{"key":"dataszm-letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"A"},{"n":"C","v":"C"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]}
		],
		"动画片":[
		{"key":"datafl-sc","name":"类型","value":[{"n":"全部","v":""},{"n":"亲子","v":"亲子"},{"n":"搞笑","v":"搞笑"},{"n":"冒险","v":"冒险"},{"n":"动作","v":"动作"},{"n":"宠物","v":"宠物"},{"n":"体育","v":"体育"},{"n":"益智","v":"益智"},{"n":"历史","v":"历史"},{"n":"教育","v":"教育"},{"n":"校园","v":"校园"},{"n":"言情","v":"言情"},{"n":"武侠","v":"武侠"},{"n":"经典","v":"经典"},{"n":"未来","v":"未来"},{"n":"古代","v":"古代"},{"n":"神话","v":"神话"},{"n":"真人","v":"真人"},{"n":"励志","v":"励志"},{"n":"热血","v":"热血"},{"n":"奇幻","v":"奇幻"},{"n":"童话","v":"童话"},{"n":"剧情","v":"剧情"},{"n":"夺宝","v":"夺宝"},{"n":"其他","v":"其他"}]},
		{"key":"datadq-area","name":"地区","value":[{"n":"全部","v":""},{"n":"中国大陆","v":"中国大陆"},{"n":"美国","v":"美国"},{"n":"欧洲","v":"欧洲"}]},
		{"key":"dataszm-letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"A"},{"n":"C","v":"C"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]}
		],
		"纪录片":[
		{"key":"datapd-channel","name":"频道","value":[{"n":"全部","v":""},{"n":"CCTV-1 综合","v":"CCTV-1综合"},{"n":"CCTV-2 财经","v":"CCTV-2财经"},{"n":"CCTV-3 综艺","v":"CCTV-3综艺"},{"n":"CCTV-4 中文国际","v":"CCTV-4中文国际(亚)"},{"n":"CCTV-5 体育","v":"CCTV-5体育"},{"n":"CCTV-6 电影","v":"CCTV-6电影"},{"n":"CCTV-7 国防军事","v":"CCTV-7军事农业"},{"n":"CCTV-8 电视剧","v":"CCTV-8电视剧"},{"n":"CCTV-9 纪录","v":"CCTV-9纪录"},{"n":"CCTV-10 科教","v":"CCTV-10科教"},{"n":"CCTV-11 戏曲","v":"CCTV-11戏曲"},{"n":"CCTV-12 社会与法","v":"CCTV-12社会与法"},{"n":"CCTV-13 新闻","v":"CCTV-13新闻"},{"n":"CCTV-14 少儿","v":"CCTV-14少儿"},{"n":"CCTV-15 音乐","v":"CCTV-15音乐"},{"n":"CCTV-17 农业农村","v":"CCTV-17农业农村高清"}]},
		{"key":"datafl-sc","name":"类型","value":[{"n":"全部","v":""},{"n":"人文历史","v":"人文历史"},{"n":"人物","v":"人物"},{"n":"军事","v":"军事"},{"n":"探索","v":"探索"},{"n":"社会","v":"社会"},{"n":"时政","v":"时政"},{"n":"经济","v":"经济"},{"n":"科技","v":"科技"}]},
		{"key":"datanf-year","name":"年份","value":[{"n":"全部","v":""},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"}]},
		{"key":"dataszm-letter","name":"字母","value":[{"n":"全部","v":""},{"n":"A","v":"A"},{"n":"C","v":"C"},{"n":"E","v":"E"},{"n":"F","v":"F"},{"n":"G","v":"G"},{"n":"H","v":"H"},{"n":"I","v":"I"},{"n":"J","v":"J"},{"n":"K","v":"K"},{"n":"L","v":"L"},{"n":"M","v":"M"},{"n":"N","v":"N"},{"n":"O","v":"O"},{"n":"P","v":"P"},{"n":"Q","v":"Q"},{"n":"R","v":"R"},{"n":"S","v":"S"},{"n":"T","v":"T"},{"n":"U","v":"U"},{"n":"V","v":"V"},{"n":"W","v":"W"},{"n":"X","v":"X"},{"n":"Y","v":"Y"},{"n":"Z","v":"Z"},{"n":"0-9","v":"0-9"}]}
		],
		"特别节目":[
		{"key":"datapd-channel","name":"频道","value":[{"n":"全部","v":""},{"n":"CCTV-1 综合","v":"CCTV-1综合"},{"n":"CCTV-2 财经","v":"CCTV-2财经"