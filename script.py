import re
import json
import time
import operator
import os

import dbHandler
import config

from threading import Thread
from distutils.dir_util import copy_tree
from urllib.request import urlopen
from collections import namedtuple


try:
    urlopen('http://google.com')
except:
    print('(!) Check Internet connection. Exit.')
    exit()

if not os.path.exists(config.filename):
    print('File ' + config.filename + ' doesn\'t exist')
    exit()


time_start = time.time()

API_BASE_URL = "http://api.ipstack.com/"
API_ACCESS_KEY = config.key

pattern_ip = re.compile(r"\d*\.\d*\.\d*\.\d*")
pattern_date = re.compile(r"\d*-\d*-\d* \d*:\d*:\d*")
pattern_location = re.compile(r"\.com/(.*)")

pattern_hour = re.compile(r"\d+-\d+-\d+ \d+")

pattern_cart = re.compile(r"cart\?")
pattern_goodsId = re.compile(r"goods_id=(\d+)")
pattern_amount = re.compile(r"amount=(\d+)")
pattern_cartIdFromCart = re.compile(r"cart_id=(\d+)")

pattern_pay = re.compile(r"pay\?")
pattern_userId = re.compile(r"user_id=(\d+)")
pattern_cartIdFromPay = pattern_cartIdFromCart

pattern_successPay = re.compile(r"success_pay_")
pattern_cartIdFromSuccessPay = re.compile(r"success_pay_(.*)\/")

ParsedItem = namedtuple('ParsedItem', 'date ip location')
Cart = namedtuple('Cart', 'date ip goods_id amount cart_id')
Pay = namedtuple('Pay', 'date ip user_id cart_id')
SuccessPay = namedtuple('SuccessPay', 'date ip cart_id')
IP = namedtuple('IP', 'ip country')
Good = namedtuple('Good', 'title categorie')
Action = namedtuple('Action', 'date action ip')

parsed_data = []

successPays = []
pays = []
carts = {}
goods = []
categories = []
actions = []
unique_ip_list = []

load_info = {}

ip_and_country_done = {}

topOfCountries = {}
topOfCategories = {}

with open(config.filename, 'r') as file:
    line = file.readline()
    while line:
        ip = pattern_ip.search(line).group()
        if ip not in unique_ip_list:
            unique_ip_list.append(ip)
        line = file.readline()

def getJSON(url):
    content = urlopen(url).read()
    j = json.loads(content)
    return j
    
def getCountry(ip):
    request = API_BASE_URL + ip + '?fields=country_name&access_key=' + API_ACCESS_KEY
    response = getJSON(request)
    country = response['country_name']
    return country

def getMultipleCountries(startIndex, endIndex):
    for x in range(startIndex, endIndex):
        try:
            ip = unique_ip_list[x]
            country = str(getCountry(ip))
            ip_and_country_done[ip] = country
        except:
            print('Error')

def initAllIPs():
    count = len(unique_ip_list)
    oneStep = count // 10
    threads = None
    if count > 10:
        if count % 10 == 0:
            threads = [
                Thread(target=getMultipleCountries, args=(0, oneStep)),
                Thread(target=getMultipleCountries, args=(oneStep, oneStep * 2)),
                Thread(target=getMultipleCountries, args=(oneStep * 2, oneStep * 3)),
                Thread(target=getMultipleCountries, args=(oneStep * 3, oneStep * 4)),
                Thread(target=getMultipleCountries, args=(oneStep * 4, oneStep * 5)),
                Thread(target=getMultipleCountries, args=(oneStep * 5, oneStep * 6)),
                Thread(target=getMultipleCountries, args=(oneStep * 6, oneStep * 7)),
                Thread(target=getMultipleCountries, args=(oneStep * 7, oneStep * 8)),
                Thread(target=getMultipleCountries, args=(oneStep * 8, oneStep * 9)),
                Thread(target=getMultipleCountries, args=(oneStep * 9, oneStep * 10 + 1))
            ]
        else:
            threads = [
                Thread(target=getMultipleCountries, args=(0, oneStep)),
                Thread(target=getMultipleCountries, args=(oneStep, oneStep * 2)),
                Thread(target=getMultipleCountries, args=(oneStep * 2, oneStep * 3)),
                Thread(target=getMultipleCountries, args=(oneStep * 3, oneStep * 4)),
                Thread(target=getMultipleCountries, args=(oneStep * 4, oneStep * 5)),
                Thread(target=getMultipleCountries, args=(oneStep * 5, oneStep * 6)),
                Thread(target=getMultipleCountries, args=(oneStep * 6, oneStep * 7)),
                Thread(target=getMultipleCountries, args=(oneStep * 7, oneStep * 8)),
                Thread(target=getMultipleCountries, args=(oneStep * 8, oneStep * 9)),
                Thread(target=getMultipleCountries, args=(oneStep * 9, oneStep * 10)),
                Thread(target=getMultipleCountries, args=(oneStep * 10, oneStep * 10 + (count % 10)))
            ]

        print('Initializing of IP addresses...')
        for t in threads:
            t.start()

    for t in threads:
        t.join()

    with open('ips.json', 'w+') as file:
        file.write(json.dumps(ip_and_country_done))
    print('Initializing done')


print('Parsing logs...')

if os.path.exists('ips.json'):
    with open('ips.json', 'r') as file:
        j = json.load(file)
        for x in j:
            ip_and_country_done[x] = j[x]
            
        print('Locations of IPs already known, skip')
else:
    initAllIPs()

with open(config.filename, 'r') as file:
    line = file.readline()
    while line:
        ip = pattern_ip.search(line).group()
        date = pattern_date.search(line).group()
        location = pattern_location.search(line).group(1)

        parsed_data.append(ParsedItem(date, ip, location))

        country = ip_and_country_done.get(str(ip))

        if topOfCountries.get(str(country)):
            topOfCountries[str(country)] += 1
        else:
            topOfCountries[str(country)] = 1

        isSuccessPay = pattern_successPay.search(location)
        if isSuccessPay:
            cart_id = pattern_cartIdFromSuccessPay.search(location).group(1)

            successPay = SuccessPay(date, ip, cart_id)
            successPays.append(successPay)

            actions.append(Action(date, "Success Pay#cart" + str(cart_id), ip))

        isPay = pattern_pay.search(location)
        if isPay:
            cart_id = pattern_cartIdFromPay.search(location).group(1)
            user_id = pattern_userId.search(location).group(1)

            pay = Pay(date, ip, user_id, cart_id)

            pays.append(pay)

            actions.append(Action(date, 'Payting#cart' + cart_id, ip))


        isCart = pattern_cart.search(location)
        if isCart:
            goods_id = pattern_goodsId.search(location).group(1)
            amount = pattern_amount.search(location).group(1)
            cart_id = pattern_cartIdFromCart.search(location).group(1)

            cart = Cart(date, ip, goods_id, amount, cart_id)
            carts[cart_id] = cart

            actions.append(Action(date, 'In Cart#cart' + cart_id, ip))

        if not location:
            actions.append(Action(date, 'On main page', ip))

        if not isCart and not isPay and not isSuccessPay and location:
            x = location.split('/')
            if len(x) == 3:
                categorie = str(x[0])
                good = x[1]

                country = str(country)

                if topOfCategories.get(categorie):
                    if topOfCategories[categorie][0].get(country):
                        topOfCategories[categorie][0][country] += 1
                    else:
                        topOfCategories[categorie][0][country] = 1
                else:
                    topOfCategories[categorie] = [{country : 1}]

                if Good(good, categorie) not in goods:
                    goods.append(Good(good, categorie))
                actions.append(Action(date, 'On goods#' + good, ip))
            if len(x) == 2:
                if x[0] not in categories:
                    categories.append(x[0])
                actions.append(Action(date, 'In categorie#' + x[0], ip))
            

        line = file.readline()

print('Parsing done')

def getTopOfCategores():
    for x in topOfCategories:
        sortedt = sorted(topOfCategories.get(x)[0].items(), key=operator.itemgetter(1))
        sortedt.reverse()
        topOfCategories[x] = sortedt
    
    return topOfCategories

def getTopOfActions():
    sortedt = sorted(topOfCountries.items(), key=operator.itemgetter(1))
    sortedt.reverse()
    return sortedt
  

def genCategories():
    j = json.dumps(categories)
    if not os.path.exists('reports'):
        os.mkdir('reports')
    with open('reports/categories.json', 'w+') as file:
        file.write(j)
    print('Categories recorded')

#########################
#
#   ГЕНЕРАТОР ОТЧЕТОВ
#
#########################

def genReport(reportNumber):
    if not os.path.exists('reports'):
        os.mkdir('reports')
    executed = False

    if reportNumber == 1:

        result = []
        data = getTopOfActions()
        with open('reports/report1.json', 'w+') as file:
            for x in data:
                result.append({
                    'country_name': x[0],
                    'count': x[1]
                })

            j = json.dumps(result)
            file.write(j)
        print('Report 1 has been created')
        executed = True

    if reportNumber == 2:
        data = getTopOfCategores()
        t = json.dumps(data)
        with open('reports/report2.json', 'w+') as file:
            file.write(t)
        print('Report 2 has been created')
        executed = True

    if reportNumber == 4:

        reqCount = 0

        for x in parsed_data:
            hour = pattern_hour.search(x.date).group()
            
            if load_info.get(hour):
                load_info[hour] += 1
            else:
                load_info[hour] = 1

        for x in load_info:
            reqCount += load_info.get(x)
        
        averageReqCount = reqCount / len(load_info)

        result = {
            'average_request_count': round(averageReqCount, 2)
        }

        with open('reports/report4.json', 'w+') as file:
            file.write(json.dumps(result))
        print('Report 4 has been created')
        executed = True

    if not executed:
        print('I can make report 1, 2 or 4.')

genCategories()
genReport(1)
genReport(2)
genReport(4)

print('Creating actions table')
dbHandler.createActionsTable()
print('Creating goods table')
dbHandler.createGoodsTable()
print('Creating transactions table')
dbHandler.createTransactionsTable()
print('Tables created. Pushing everything...')


for x in goods:
    good_title = x.title
    good_categorie = x.categorie
    dbHandler.createGoodsItem(good_title, good_categorie)

for x in successPays:
    date = x.date
    ip = x.ip
    cart_id = x.cart_id
    
    cartInfo = carts.get(cart_id)

    amount = cartInfo.amount
    goods_id = cartInfo.goods_id


    dbHandler.createTransactionItem(date, goods_id, amount, cart_id, ip)

for x in actions:
    date = x.date
    action = x.action
    ip = x.ip
    country = ip_and_country_done[ip]
    dbHandler.createActionItem(date, action, ip, country)

dbHandler.save()

print('Pushed!')

copy_tree('reports', 'Web/reports')
print('Reports copied to Web. Start Web folder on web server.')


end_time = time.time()
difference = str(end_time - time_start)

print()
print('General executing time: ' + difference + 's')
print()
print('Created by Grinvald Vyacheslav vk.com/gora_pl')

print()