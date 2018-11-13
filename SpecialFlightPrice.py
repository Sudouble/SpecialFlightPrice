# -*- coding: utf-8 -*-
import datetime
import json
import urllib
import re
import xml.etree.cElementTree as ET
import sys

default_encoding = 'utf-8'
reload(sys)
sys.setdefaultencoding(default_encoding)


def getdate(startdate, enddate):
    # url = 'https://sjipiao.alitrip.com/search/cheapFlight.htm?startDate=%s&endDate=%s&' \
    #      'routes=BJS-&_ksTS=1469412627640_2361&callback=jsonp2362&ruleId=99&flag=1' % (startdate, enddate)
    url = 'https://r.fliggy.com/rule/domestic?startDate=%s&' \
          'endDate=%s&routes=BJS-&' \
          '_ksTS=1542114152926_1252&callback=jsonp2362&ruleId=99&flag=1' % (startdate, enddate)
    price_html = urllib.urlopen(url).read().strip()

    pattern = r'jsonp2362\((.+)\)'
    re_rule = re.compile(pattern)
    json_data = re.findall(pattern, price_html)[0]
    # print(json_data)
    
    price_json = json.loads(json_data)

    flights = price_json['data']['flights']  # flights Info
    return flights


# 获取目的地的省份
def get_Target(cityname):
    tree = ET.ElementTree(file='province_city.xml')
    root = tree.getroot()

    name = dig(root, cityname)
    for item in name:
        for province in name[item]:
            return province


def dig(tree, cityname):
    findedname = {}
    key = tree.attrib['name']

    value = []
    for elem in tree:
        if cityname in elem.attrib['name']:
            value.append(elem.attrib['name'])
            findedname[key] = value

        currentname = dig(elem, cityname)
        if currentname != {}:
            findedname[key] = currentname
    return findedname


# 将特价航班按照省份归类
def flights_sort(flights):
    names = {}
    for f in flights:
        value = []
        province = get_Target(f['arrName'])
        if not names.has_key(province):
            value.append(f)
            names[province] = value
        else:
            value = names[province]
            value.append(f)
            names[province] = value
    return names


# 设定目的地
def set_target(name):
    if type(name) == str:
        return get_Target(name).encode('utf-8')
    else:
        provinces = []
        for item in name:
            provinces.append(get_Target(item).encode('utf-8'))
        return provinces


# 输出目的地及其附近的航班信息
def printTargetInfo(sorted_flights, targetName):
    print
    print '*****************targetInfo*****************'
    currentName = set(targetName)
    for province in sorted_flights:
        for targetProvince in currentName:
            if targetProvince == province:
                print_trip(sorted_flights[province], province)


# 输出所有航班信息
def print_all_trip(flights):
    for province in flights:
        print_trip(flights[province], province)


# 输出目的地航班信息
def print_trip(flight, province):
        print '===============Province:%s===============' % province
        for f in flight:
            source = '从：%s-' % f['depName']
            dest = '到：%s\t' % f['arrName']
            price = '\t价格：%s%s(折扣:%s)\t' % ((f['price']), f['priceDesc'], f['discount'])
            depart_date = '\t日期：%s' % f['depDate']
            print source + dest + price + depart_date


def task_query_flight():
    delay = int(raw_input('Enter the Day after: '))
    target = ['南京']
    today = datetime.date.today()
    enddate = today + datetime.timedelta(delay)
    endstr = str(enddate)
    print str(today) + ' To ' + endstr

    province = set_target(target)
    flights = getdate(today, enddate=endstr)
    flights = flights_sort(flights)
    print_all_trip(flights)
    printTargetInfo(flights, province)

if __name__ == '__main__':
    task_query_flight()
