#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 百度贴吧爬虫类
# 主要优化：每层信息加了作者、发布时间，文件写入完毕关闭了输出流
import urllib.request
import urllib.error
import ssl
import re

import SimpleSpiders.Tool


# 百度贴吧爬虫类
class BDTBSpider:
    # 初始化，传入基地址，是否只看楼主的参数
    def __init__(self, baseUrl, seeLZ='0', floorTag='1', path=''):
        # base链接地址
        self.baseUrl = baseUrl
        # 是否只看楼主
        self.seeLZ = '?see_lz=' + str(seeLZ)
        # HTML标签剔除工具类对象
        self.tool = SimpleSpiders.Tool.Tool()
        # 全局file变量，文件写入操作对象
        self.file = None
        # 楼层标号，初始为1
        self.floor = 1
        # 默认的标题，如果没有成功获取到标题的话则会用这个标题
        self.defaultTitle = "百度贴吧"
        # 是否写入楼分隔符的标记
        self.floorTag = str(floorTag)
        # 保存路径
        self.path = path
        ssl._create_default_https_context = ssl._create_unverified_context

    # 传入页码，获取该页帖子的代码
    def getPage(self, pageNum):
        try:
            # 构建URL
            url = self.baseUrl + self.seeLZ + '&pn=' + str(pageNum)
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            # 返回UTF-8格式编码内容
            return response.read().decode('utf-8')
        # 无法连接，报错
        except urllib.error.URLError as e:
            if hasattr(e, 'reason'):
                print('连接百度贴吧失败,错误原因:', e.reason)
                return

    # 获取帖子标题
    def getTitle(self, page):
        # 得到标题的正则表达式
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>', re.S)
        result = re.search(pattern, page)
        if result:
            # 如果存在，则返回标题
            return result.group(1).strip()
        else:
            return

    # 获取帖子一共有多少页
    def getPageNum(self, page):
        # 获取帖子页数的正则表达式
        pattern = re.compile('回复贴，共<span.*?>(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            return result.group(1).strip()
        else:
            return

    # 获取每一层楼的内容,传入页面内容
    def getContent(self, page):
        # 匹配所有楼层的内容,item[0]是作者，item[1]是内容,item[2]是发布时间
        pattern = re.compile(
            '<li class="d_name".*?p_author_name.*?>(.*?)</a>.*?<div id="post_content_.*?>(.*?)</div>.*?楼</span><span class="tail-info">(.*?)</span>',
            re.S)
        items = re.findall(pattern, page)
        contents = []
        for item in items:
            # 将文本进行去除标签处理，同时在前后加入换行符
            content = '\n' + '本楼作者：' + item[0].strip() + '\t发布时间：' + item[2].strip() + '\n' + self.tool.replace(
                item[1]) + '\n'
            contents.append(content)
        return contents

    def setFileTitle(self, title):
        # 如果标题不是为None，即成功获取到标题
        if title is not None:
            self.file = open(self.path + title + '.txt', 'w+')
        else:
            self.file = open(self.path + self.defaultTitle + '.txt', 'w+')

    def writeData(self, contents):
        # 向文件写入每一楼的信息
        for item in contents:
            # 楼之间的分隔符
            if self.floorTag == '1':
                floorLine = '\n' + str(
                    self.floor) + '楼-----------------------------------------------------------------------------------------\n'
                self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1

    def start(self):
        indexPage = self.getPage(1)
        if indexPage is None:
            print('连接失败，请重试')
            return
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        if pageNum is None:
            print('URL已失效，请重试')
            return
        try:
            print('该帖子共有' + str(pageNum) + '页')
            for i in range(1, int(pageNum) + 1):
                print('正在写入第' + str(i) + '页数据')
                page = self.getPage(i)
                contents = self.getContent(page)
                self.writeData(contents)
        # 出现写入异常
        except IOError as e:
            print('写入异常，原因：' + str(e))
        finally:
            print('写入任务完成')
            # 关闭写入流
            self.file.close()


print('请输入帖子代号')
baseURL = 'http://tieba.baidu.com/p/' + str(input('https://tieba.baidu.com/p/\n'))
seeLZ = input("是否只获取楼主发言，是输入1，否输入0\n")
floorTag = input("是否写入楼层信息，是输入1，否输入0\n")
path = input("请输入保存路径，以/结尾(直接回车保存在当前路径)：\n")
bdtb = BDTBSpider(baseURL, seeLZ, floorTag, path)
bdtb.start()
