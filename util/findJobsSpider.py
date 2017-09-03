#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import re
import ssl

import requests
from bs4 import BeautifulSoup

'''
    最近也是蛮慌的于是写了个抓取牛客网讨论区招聘信息的爬虫，基于Python3，依赖BeautifulSoup4和requests。
    功能很简单，就是抓取帖子信息以当前时间为文件名保存下来，默认会保存在 用户目录/findJobs 下面。第一次会
    抓取近7天数据，第二次开始只会抓取从上次抓取时间那天开始的数据。
    (因为刚开始练python所以代码丑了点_(:з」∠)_...)
    待更新：1.更加精确的抓取（目前第二次抓取会连上次抓取当天的帖子重复抓取一遍）
    2.支持抓取指定时间之后的帖子
    3.多线程抓取提高速度（考虑中，如果抓取速度太快可能会被封）
    4.支持抓取指定版块（其实现在就支持，只是没有提示）
'''


class FindJobs:

    # 初始化一些必要参数
    def __init__(self, pType='7', pPath=None):
        # 牛客讨论区
        self.__baseUrl = 'https://www.nowcoder.com'
        self.__discussUrl = 'https://www.nowcoder.com/discuss'
        # get请求跟的信息，type=7表示招聘信息，order=3表示按最新发布排列
        self.__params = {'order': '3', 'type': str(pType)}
        # 设置headers伪装成正常请求，但是牛客好像目前没有做反爬措施
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36'}
        # 保存的文件夹
        self.__pPath = pPath
        # 每次抓取最终保存的文件路径
        self.__fileName = None
        # 判断是否设置了保存目录，如果没有就默认保存在 用户目录 下
        if not self.__pPath:
            self.__pPath = os.path.join(os.path.expanduser('~'), 'findJobs')
        else:
            self.__pPath = os.path.join(self.__pPath, 'findJobs')
        # 创建文件夹
        if not os.path.exists(self.__pPath):
            os.makedirs(self.__pPath)
        # 忽略ssl验证
        ssl._create_default_https_context = ssl._create_unverified_context
        # 日期格式化
        self.__DATE_TIME_TEMPLATE = '%Y-%m-%d %H:%M:%S'
        self.__DATE_TEMPLATE = '%Y-%m-%d'
        self.__TIME_TEMPLATE = '%H:%M:%S'
        self.__FILE_TIME_TEMPLATE = '%Y-%m-%d %H-%M-%S'

    # 获取页面上的链接和时间
    def __getPage(self, page='1'):
        params = self.__params
        # 将post请求带上页码
        params['page'] = page
        # 当页的数据
        lists = []
        try:
            # 获取数据，解析，找到指定div
            r = requests.get(self.__discussUrl, params=params, headers=self.__headers)
            soup = BeautifulSoup(r.text, 'lxml')
            divs = soup.find_all('div', class_='discuss-detail')
            for div in divs:
                # 页面上的帖子地址是相对路径，所以这里要拼成绝对地址
                content = {'url': self.__baseUrl + str(div.div.a.get('href'))}
                # 获取时间，不得不说python的日期处理很麻烦，因为都是不可改变类型，所以想只想改变时间不改日期的话就得
                # 先转成字符串再转回来，回头可以封装个工具类
                pattern = re.compile('.*?\n(.*?)\n', re.S)
                pTime = re.search(pattern, div.find(class_='feed-tip').a.next_sibling).group(1).strip()
                # 日期格式有两种，今天的就是'今天 10:00:00'这种，而昨天及以前的就是'2018-9-1'这种
                if '今天' in pTime:
                    pattern = re.compile('.*?今天.*?(.*?)\n', re.S)
                    postTime = re.search(pattern, div.find(class_='feed-tip').a.next_sibling).group(1).strip()
                    pTime = datetime.date.today().strftime('%Y-%m-%d ') + postTime
                    pTime = datetime.datetime.strptime(pTime, self.__DATE_TIME_TEMPLATE)
                else:
                    pTime = datetime.datetime.strptime(pTime, self.__DATE_TEMPLATE)
                # 每条结果里面都保存了帖子地址和发布时间
                content['time'] = pTime
                lists.append(content)
        except requests.Timeout as e:
            print('Timeout:[%s]' % e)
        except requests.ConnectionError as e:
            print('ConnectionError:[%s]' % e)
        except requests.HTTPError as e:
            print('HTTPError:[%s]' % e)
        return lists

    # 获取帖子的具体内容
    def __getContent(self, url):
        r = requests.get(url, headers=self.__headers)
        soup = BeautifulSoup(r.text, 'lxml')
        # 获取标题、作者和发布时间，并去除前后空白
        head = soup.find('div', class_='discuss-topic-head')
        title = head.h1.get_text(strip=True)
        author = head.div.div.a.get_text(strip=True)
        time = head.div.div.div.span.get_text(strip=True)
        # time解析出来之后会有'发布于 '几个字符，这里去掉
        time = str(time)[4:].strip()
        content = soup.find('div', class_='post-topic-des')
        # 去掉js
        content.find('script').extract()
        # 获取帖子内容，用换行分割
        content = content.get_text('\n', '<br/>')
        # 拼接帖子内容
        out = '标题：' + title + '\n' + '作者：' + author + '     发布时间：' + time + '\n' + url + '\n' + content
        return out

    # 爬取规则：如果没有爬过，就爬近七天的，如果爬过，就从上次爬的那天开始爬
    def __gatherList(self, nTime, lastTime=None):
        page = 1
        # 如果没有爬取记录，就设置成从七天前开始
        if not lastTime:
            grabTime = (datetime.date.today() - datetime.timedelta(days=7)).strftime(self.__DATE_TEMPLATE)
            grabTime = datetime.datetime.strptime(grabTime, self.__DATE_TEMPLATE)
        else:
            grabTime = datetime.datetime.strptime(lastTime, self.__DATE_TIME_TEMPLATE)
            if grabTime.date() != datetime.date.today():
                grabTime = grabTime - datetime.timedelta(days=1)
        lists = []
        while True:
            pageList = self.__getPage(str(page))
            # 判断该页帖子的最后一条时间是否小于设定的抓取时间，不小于就添加进list
            if pageList[-1]['time'] >= grabTime:
                lists.extend(pageList)
                page += 1
            else:
                # 小于就从当页第一条开始判断，将大于等于抓取时间的添加进list
                num = 0
                while pageList[num]['time'] >= grabTime:
                    lists.append(pageList[num])
                    num += 1
                break
        if not lists:
            print('距离上次抓取没有新帖子了_(:з」∠)_')
            return
        # 判断置顶帖日期是否符合要求
        num = 0
        while lists[num]['time'] < grabTime:
            num += 1
        lists = lists[num:]
        # 开始写入文件
        self.__fileName = str(nTime) + '.txt'
        with open(os.path.join(self.__pPath, self.__fileName), 'w+', encoding='utf-8') as file:
            num = 1
            file.write('本次共抓取到%d条数据_(:з」∠)_\n\n' % len(lists))
            print('本次共抓取到%d条数据_(:з」∠)_' % len(lists))
            for data in lists:
                content = self.__getContent(data['url'])
                print('正在写入第%d条数据...' % num)
                file.write('第%d条：\n' % num)
                file.write(content)
                file.write('\n----------------------------------')
                file.write('\n\n\n')
                num += 1

    # 入口方法
    def start(self, fTime=None):
        # 读取上次抓取的时间
        fileName = os.path.join(self.__pPath, 'lastTime.txt')
        # 记录当前时间
        nTimeAll = datetime.datetime.now()
        nTimeAll = nTimeAll.strftime(self.__FILE_TIME_TEMPLATE)
        # w+模式会清空数据，所以如果存在文件的话需要用r+打开
        if os.path.exists(fileName):
            file = open(fileName, 'r+', encoding='utf-8')
        else:
            file = open(fileName, 'w+', encoding='utf-8')
        print('开始抓取信息...')
        if not fTime:
            fTime = file.readline()
        if fTime:
            self.__gatherList(nTimeAll, fTime)
        else:
            self.__gatherList(nTimeAll)
        # 将文件游标设置为开始，覆盖之前的时间
        file.seek(0)
        file.write(nTimeAll)
        file.close()
        if self.__fileName:
            print('抓取完成！已保存在%s' % (os.path.join(self.__pPath, self.__fileName)))

print('请输入保存路径(不需要加上findJobs，直接回车保存在默认位置)：')
path = input()
findJobs = FindJobs(pPath=path)
findJobs.start()
