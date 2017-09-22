#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import xlrd

workbook = xlrd.open_workbook('/Users/didi/Desktop/BRA Map Data.xlsx')
sheet = workbook.sheet_by_name('BRA_Region')
ans = []
for i in range(1, sheet.nrows):
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = sheet.row_values(i)
    s = "INSERT INTO `g_city` (`area`, `country_code`, `district`, `name`, `en_name`, `car_prefix`, `center_lng`, `center_lat`, `is_open`, `_create_time`, `_modify_time`, `_status`) VALUES (" + \
        row[5] + ", 55, '" + row[7] + "', '" + row[
            6] + "', '" + row[6] + "', '00', 0.000000, 0.000000, 0, '" + time + "', '" + time + "', 1);"
    ans.append(s)
with open('/Users/didi/Desktop/baxi.txt', 'w+', encoding='utf-8') as file:
    for i in ans:
        file.write(i + '\n')
