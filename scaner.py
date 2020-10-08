from time import sleep
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import json
import time
import urllib3
import os

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
                if time.time() > int(old[liga][match]['timeStart'] + 28800):
                    old[liga].pop(match)
    except AttributeError:
        pass
    return old

def addMatch(lineData, file):
    newMatches = readInfo(file)
    for liga in lineData.keys():
        for name in lineData[liga]:
            try:
                if name not in newMatches[liga]:
                    newMatches[liga][name] = lineData[liga][name]
            except KeyError:
                newMatches[liga] = {name: lineData[liga][name]}

    newMatches = clearOldLines(newMatches)
    writeInfo(newMatches, file)

def clearRamBrowser(browser):
    pid = browser.capabilities['moz:processID']
    proc_list = os.popen('tasklist /FO CSV').read()
    proc_list = proc_list.split('\n')[3:-1]
    procPidRam = {}
    [procPidRam.update({ int(i.replace('"', '').split(',')[1]) : int(i.replace('"', '').split(',')[-1][:-3].replace('я', '')) }) for i in proc_list]
    if procPidRam[pid] > 400000:
        browser.quit()

def offCompactView():
    browser.find_element_by_class_name('curcoefDropTop').click()
    sleep(0.3)
    browser.find_element_by_css_selector('ul.teo-item:nth-child(6) > li:nth-child(1)').click()
    sleep(0.2)
    browser.find_element_by_class_name('curcoefDropTop').click()

def wheel_element(element, deltaY = 300, offsetX = 0, offsetY = 0):
  element._parent.execute_script("""
    var element = arguments[0];
    var deltaY = arguments[1];
    var box = element.getBoundingClientRect();
    var clientX = box.left + (arguments[2] || box.width / 2);
    var clientY = box.top + (arguments[3] || box.height / 2);
    var target = element.ownerDocument.elementFromPoint(clientX, clientY);

    for (var e = target; e; e = e.parentElement) {
      if (e === element) {
        target.dispatchEvent(new MouseEvent('mouseover', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new MouseEvent('mousemove', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new WheelEvent('wheel',     {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY, deltaY: deltaY}));
        return;
      }
    }    
    return "Element is not interactable";
    """, element, deltaY, offsetX, offsetY)






oldLiveMatches = {}
newMatches = {}

def getLive():

    liveData = {}
    try:

        ligsLeft = browser.find_elements_by_class_name('link--labled')
        if len(ligsLeft) == 0:
            return {}
        wheel_element(ligsLeft[0])
        for ligLeft in ligsLeft:
            print(ligLeft.text)

            ligLeft.click()
            wheel_element(ligLeft, deltaY=40)

            sleep(0.5)

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

                        print(liga)
                        print(name)
                        print(total)
                        print('\n')

                        while 1:
                            try:
                                liveData[liga][name] = {'firstKoef': firstKoef, 'secondKoef': secondKoef, 'timeAdd': time.time(), 'timeStart':timeStart, 'total': total}
                                break
                            except KeyError:
                                liveData[liga] = {name: {}}

                ligLeft.click()
                sleep(0.5)

            except IndexError:
                ligLeft.click()
                continue




    except (common.exceptions.NoSuchElementException, common.exceptions.StaleElementReferenceException):
        browser.refresh()
        time.sleep(5)

    return liveData


p = 0
while 1:
    try:
        browser = webdriver.Firefox()
        browser.set_window_size(1200, 2000)
        browser.get('https://one-xotsvo.world/ru/line/Tennis/')
        sleep(5)
        offCompactView()
        lineData = getLive()
        browser.quit()
        print('Информация из линии: ', lineData)
        addMatch(lineData, 'lineTennis.json')
    except:
        try:
            browser.quit()
        except:
            pass


'''
1 добавляем матчи в dict
2 ждем пока появится новый матч -
3 добавляем новый матч в файл для api
4 не изменяем полученные данные в api
'''