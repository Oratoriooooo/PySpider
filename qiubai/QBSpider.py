#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import ssl
import urllib.request
import urllib.error

__author__ = 'aa'


# 糗百爬虫类
class QBSpider:
    # 初始化一些数据
    def __init__(self):
        self.pageIndex = 1
        # 初始化headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36'}
        # 存放段子的变量，每一个元素是每一页的段子们
        self.stories = []
        # 存放程序是否继续运行的变量
        self.enable = False
        # python2.7.9之后引入了一个新特性，当使用urllib.urlopen打开一个https链接时，会验证一次SSL证书，如果是自签名证书就会报错，
        # 所以这里全局取消验证
        ssl._create_default_https_context = ssl._create_unverified_context

    # 传入某一页的索引获得页面代码
    def getPage(self, pageIndex):
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
            # 构建请求的request
            request = urllib.request.Request(url, headers=self.headers)
            # 利用urlopen获取页面代码
            response = urllib.request.urlopen(request)
            # 将页面转化为UTF-8编码
            content = response.read().decode('utf-8')
            return content
        except urllib.error.URLError as e:
            if hasattr(e, 'reason'):
                print('连接糗事百科失败，错误原因：', e.reason)
                return None

    # 传入某一页代码，返回本页不带图片的段子列表
    def getPageItems(self, pageIndex):
        content = self.getPage(pageIndex)
        if not content:
            print('页面加载失败！')
            return None
        pattern = re.compile(
            'author clearfix">.*?<h2>(.*?)</h2>.*?<div.*?content">.*?<span>(.*?)</span>.*?gif\s-->(.*?)<!--.*?number">(.*?)</i>',
            re.S)
        items = re.findall(pattern, content)
        # 用来存储每页的段子们
        pageStories = []
        # 遍历正则表达式匹配的信息
        for item in items:
            # 是否含有图片
            haveImg = re.search('img', item[2])
            # 如果不含有图片，把它加入list中
            if not haveImg:
                replaceBR = re.compile('<br/>')
                text = re.sub(replaceBR, '\n', item[1])
                # item[0]是一个段子的发布者，item[1]是内容，item[2]是图片,item[3]是点赞数
                pageStories.append([item[0].strip(), text.strip(), item[3].strip()])
        return pageStories

    # 加载并提取页面的内容，加入到列表中
    def loadPage(self):
        # 如果当前未看的页数少于2页，则加载新一页
        if self.enable == True:
            if len(self.stories) < 2:
                # 获取新一页
                pageStories = self.getPageItems(self.pageIndex)
                # 将该页的段子存放到全局list中
                if pageStories:
                    # 获取完之后页码索引加一，表示下次读取下一页
                    self.stories.append(pageStories)
                    self.pageIndex += 1

    # 调用该方法，每次敲回车打印输出一个段子
    def getOneStory(self, pageStories, page):
        # 遍历一页的段子
        for story in pageStories:
            # 等待用户输入，注意由于python3将raw_input()改为了input()，所以不能直接用input当做变量名
            input1 = input()
            self.loadPage()
            # 如果输入Q则程序结束
            if input1 == 'q':
                self.enable = False
                return
            print('第%d页\t发布人:%s\t赞:%s\n%s' % (page, story[0], story[2], story[1]))

    # 开始方法
    def start(self):
        print('正在读取糗事百科,按回车查看新段子，Q退出')
        # 使变量为True，程序可以正常运行
        self.enable = True
        # 先加载一页内容
        self.loadPage()
        # 局部变量，控制当前读到了第几页
        nowPage = 0
        while self.enable:
            if len(self.stories) > 0:
                # 从全局list中获取一页的段子
                pageStories = self.stories[0]
                # 当前读到的页数加一
                nowPage += 1
                # 将全局list中第一个元素删除，因为已经取出
                del self.stories[0]
                # 输出该页的段子
                self.getOneStory(pageStories, nowPage)


spider = QBSpider()
spider.start()
