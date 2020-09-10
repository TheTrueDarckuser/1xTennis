from time import sleep
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import json
import time
import urllib3

# print('Запуск сканера через 1,5 минуты')
# time.sleep(200)


try:
    file = open("lineTennis.json", 'x')
    file.close()
except FileExistsError:
    pass

def readInfo(file):
    with open(file, 'r') as file:
        try:
            oldInformation = json.load(file)
        except:
            oldInformation = {}
    return oldInformation

def writeInfo(info, nameFile):
    with open(nameFile, 'w') as file:
        json.dump(info, file)

def compareDict(new, old):
    newDict = {}
    for i in new:
        for k in new[i]:
            try:
                old[i][k], "OLD"
            except KeyError:
                while 1:
                    try:
                        newDict[i][k] = new[i][k]
                        break
                    except KeyError:
                        newDict[i] = {}
    return newDict

def clearOldLines(old):
    try:
        for liga in list(old.keys()):
            for match in list(old[liga].keys()):
                if time.time() > int(old[liga][match]['timeStart'] + 18000):
                    old[liga].pop(match)
    except AttributeError:
        pass
    return old



browser = webdriver.Firefox()
browser.get('https://1xstavka.ru/ru/line/Tennis/')
sleep(5)

oldLiveMatches = {}
newMatches = {}

def getLive():

    liveData = {}
    try:
        games = browser.find_element_by_id('games_content').find_element_by_xpath('div/div[2]/div')

        games = games.find_elements_by_xpath('div')

        for game in games:
            game = game.find_elements_by_xpath('div')
            try:
                liga = game[0].text.split('\n')[0]
            except AttributeError:
                continue
            matches = game[1:]
            for match in matches:
                name = match.find_element_by_class_name('c-events__name').text
                # url = match.find_element_by_class_name('c-events__name').get_attribute('href')
                firstKoef = match.find_elements_by_class_name('c-bets__bet')[0].text
                if firstKoef == '-':
                    continue
                secondKoef = match.find_elements_by_class_name('c-bets__bet')[2].text
                if secondKoef == '-':
                    continue
                total = match.find_elements_by_class_name('c-bets__bet')[4].text
                if total == '-':
                    continue
                timeStart = match.find_element_by_class_name('c-events__time-info').text

                timeStart = time.mktime(time.strptime(timeStart + ' ' + str(time.localtime().tm_year), '%d.%m %H:%M %Y'))




                # print(liga)
                # print(name)
                # print(total)
                # print(score)
                # print(setsInLiveFirst)
                # print(setsInLiveSecond)
                # print(url)
                # print('\n\n')

                while 1:
                    try:
                        liveData[liga][name] = {'firstKoef': firstKoef, 'secondKoef': secondKoef, 'timeAdd': time.time(), 'timeStart':timeStart, 'total': total}
                        break
                    except KeyError:
                        liveData[liga] = {name: {}}


    except (common.exceptions.NoSuchElementException, common.exceptions.StaleElementReferenceException):
        browser.refresh()
        time.sleep(5)

    return liveData

liveData = getLive()
# print(liveData)
oldLiveMatches.update(liveData)


p = 0
while 1:
    try:
        liveData = getLive()
    except (common.exceptions.WebDriverException, common.exceptions.NoSuchWindowException):
        try:
            browser.quit()
        except:
            pass
        browser = webdriver.Firefox()
        browser.get('https://1xstavka.ru/ru/line/Tennis/')
        sleep(5)
    print(liveData)
    newMatches.update(compareDict(liveData, oldLiveMatches))
    dataFromFile = readInfo('lineTennis.json')
    dataFromFile = clearOldLines(dataFromFile)
    writeInfo(dataFromFile, 'lineTennis.json')
    #Новый матч дообавляем в lineTennis.json и добавляем в oldLive matches
    if len(newMatches) > 0:
        dataFromFile = readInfo('lineTennis.json')
        dataFromFile.update(newMatches)
        writeInfo(dataFromFile, 'lineTennis.json')
        oldLiveMatches.update(newMatches)
        newMatches = {}
    p += 1
    if p > 20000:
        try:
            browser.quit()
        except:
            pass
        browser = webdriver.Firefox()
        browser.get('https://1xstavka.ru/ru/line/Tennis/')
        sleep(5)