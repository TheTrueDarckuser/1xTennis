from time import sleep
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import json
import time
import urllib3
import os
import configparser

configFile = "config.ini"
try:
    def get_config(path):
        config = configparser.ConfigParser()
        config.read(path)
        return config

    def update_setting(path, section, setting, value):
        config = get_config(path)
        config.set(section, setting, value)
        with open(path, "w") as config_file:
            config.write(config_file)

    update_setting(configFile, 'PID', 'flask', str(os.getpid()))
except:
    pass


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

def clearRamBrowser(browser):
    pid = browser.capabilities['moz:processID']
    proc_list = os.popen('tasklist /FO CSV').read()
    proc_list = proc_list.split('\n')[3:-1]
    procPidRam = {}
    [procPidRam.update({ int(i.replace('"', '').split(',')[1]) : int(i.replace('"', '').split(',')[-1][:-3].replace('я', '')) }) for i in proc_list]
    if procPidRam[pid] > 400000:
        browser.quit()


browser = webdriver.Firefox()
browser.get('https://1xstavka.ru/ru/live/Tennis/')
sleep(5)

oldLiveMatches = {}
newMatches = {}

def getLive():
    liveData = {}
    try:
        games = browser.find_element_by_id('games_content').find_element_by_xpath('div/div/div[1]')
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

                score = match.find_elements_by_class_name('c-events-scoreboard__cell--all')
                score = [i.text for i in score]
                if score != ['0', '(0)', '0', '(0)']:
                    continue




                print(liga)
                print(name)
                # print(total)
                # print(score)
                # print(setsInLiveFirst)
                # print(setsInLiveSecond)
                # print(url)
                print('\n\n')

                while 1:
                    try:
                        liveData[liga][name] = {'firstKoef': firstKoef, 'secondKoef': secondKoef, 'timeStart': time.time(), 'total': total}
                        break
                    except KeyError:
                        liveData[liga] = {name: {}}


    except (common.exceptions.NoSuchElementException, common.exceptions.StaleElementReferenceException):
        browser.refresh()
        time.sleep(5)

    # print(liveData)
    return liveData

liveData = getLive()
print(liveData)
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
        browser.get('https://1xstavka.ru/ru/live/Tennis/')
        sleep(5)
    # print(liveData)
    newMatches.update(compareDict(liveData, oldLiveMatches))
    dataFromFile = readInfo('lineTennis.json')
    dataFromFile = clearOldLines(dataFromFile)
    writeInfo(dataFromFile, 'lineTennis.json')
    #Новый матч дообавляем в line.json и добавляем в oldLive matches
    if len(newMatches) > 0:
        dataFromFile = readInfo('lineTennis.json')
        dataFromFile.update(newMatches)
        writeInfo(dataFromFile, 'lineTennis.json')
        oldLiveMatches.update(newMatches)
        newMatches = {}
    clearRamBrowser(browser)

    p += 1
    if p > 10800:
        p = 0
        try:
            browser.quit()
            sleep(15)
        except:
            pass
        browser = webdriver.Firefox()
        browser.get('https://1xstavka.ru/ru/live/Tennis/')
        sleep(5)