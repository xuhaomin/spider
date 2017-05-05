### bilibili分析

- 从网站视频排行榜 http://www.bilibili.com/ranking 抓包分析可以看到，数据来源为 http://www.bilibili.com/index/rank/all-{day}-{tid}.json 
- 其中，day为不同时间周期的排行，可选值为[1,3,7,30],即 日，三日，周，月排行；
- tid为分类id，b站分类有近百个，而加入排行的分类只有十二个，分别是{'0':'全站','1':'动画','3':'音乐', '4':'游戏','5':'娱乐','11': '连载剧集', '23': '电影', '33': '连载动画', '36': '科技','119': '鬼畜', '129': '舞蹈', '168': '国创相关'}
- 排行榜返回的json数据中，list字段包含了排行中视频的基本信息，分别有 aid：视频的ID；play：播放次数；video_review：视频评论；title：标题；mid：作者ID，duration：视频长度；others：相关视频信息。但是分析这些数据可以发现，排行榜的统计数据应该是周期内数据，不是该视频的总数据。
- 再次抓包，发现视频总的统计数据来源于 http://api.bilibili.com/archive_stat/stat?aid={aid} ，其返回数据中含有："view":播放数,"danmaku":弹幕数,"reply":评论数,"favorite":收藏,"coin":硬币,"share":分享,"now_rank":目前排名,"his_rank":历史排名
- 视频的详细页面为 http://www.bilibili.com/video/av{aid} 其中，视频的播放链接涉及到参数 cid，目前cid我只找到从详细页查找获得一个方法。由cid获得视频的下载链接再很多开源的库中都有代码，一般都涉及到appkey，应该是b站开放的api
- 从视频作者出发，抓包分析，视频作者对应的视频源自链接 http://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}}&page={page}&pagesize={pagesize} 其中mid就是视频作者ID，page 和pagesize是该ajax请求根据videos个数你所请求的分页信息。 返回的data中，有个vlist就是视频的集合，有视频的基本信息。
- vlist中字段有{"aid":视频ID,"copyright":原创/引用,"typeid":tid,"title":标题,"subtitle":副标题,"play":播放次数,"review":弹幕,"video_review":评论,"favorites":收藏,"mid":作者id,"author":作者,"description":简介,"created":发布时间,"pic":图片,"comment":评论,"length":视频长,"hide_click":false}

#### 获得cid
> cid直接对应下载链接
- 有一个特别有名的视频下载库，叫youtube-dl，链接为https://github.com/rg3/youtube-dl
- b站的相关源码 https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/bilibili.py
- 函数 _real_extract 及分析网页得出对于非'anime'（！即番剧）的 cid 获取方法,就是从视频详情页面通过两种正则匹配得到 [r'EmbedPlayer\([^)]+,\s*"([^"]+)"\)','<iframe[^>]+src="https://secure\.bilibili\.com/secure,([^"]+)"'] 当然，其实直接匹配 r'cid=(\d+)'应该也能获得
- 对于番剧，先得到番剧的seasonID 然后通过链接 http://bangumi.bilibili.com/jsonp/seasoninfo/{sID}.ver 获得相应的分集episode_id 然后通过 http://bangumi.bilibili.com/web_api/get_source POST请求 {'episode_id': episode_id} 可以得到cid

#### 从cid获得download-url
- 先得到一个 payload 'appkey={appkey}&cid={cid}&otype=json&quality=2&type=mp4' appkey是b站的appkey
- sign 签名  hashlib.md5((payload + self._BILIBILI_KEY).encode('utf-8')).hexdigest() _BILIBILI_KEY 是 b站的了一个签名
- 然后通过链接 'http://interface.bilibili.com/playurl?%s&sign=%s' % (payload, sign) 得到其中的
url字段的值，就是播放下载链接了
