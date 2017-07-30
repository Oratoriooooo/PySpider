#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re


#处理页面标签类
class Tool:
    # 去除img标签,7位长空格
    __removeImg = re.compile('<img.*?>| {7}')
    # 删除超链接标签
    __removeAddr = re.compile('<a.*?>|</a>')
    # 把换行的标签换为\n
    __replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    # 将表格制表<td>替换为\t
    __replaceTD = re.compile('<td>')
    # 把段落开头换为\n加空两格
    __replacePara = re.compile('<p.*?>')
    # 将换行符或双换行符替换为\n
    __replaceBR = re.compile('<br><br>|<br>')
    # 将其余标签剔除
    __removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.__removeImg, "", x)
        x = re.sub(self.__removeAddr, "", x)
        x = re.sub(self.__replaceLine, "\n", x)
        x = re.sub(self.__replaceTD, "\t", x)
        x = re.sub(self.__replacePara, "\n    ", x)
        x = re.sub(self.__replaceBR, "\n", x)
        x = re.sub(self.__removeExtraTag, "", x)
        # strip()将前后多余内容删除
        return x.strip()