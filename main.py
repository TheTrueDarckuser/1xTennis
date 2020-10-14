from time import sleep
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from urllib3 import exceptions
import json
import time
import datetime
import requests
import winsound
import os


url = 'https://one-xotsvo.world/ru'
# url = 'https://bet1x95202.com/ru'
login = ''
password = ''
amount = 375
autoLogin = True
delLigs = ['winners cup', 'mixed', 'микст', 'сетка кап', 'пары', 'Smash Cup', 'Neva Open', 'VS Open', "Россия. Мастерс", "Россия. Мастерс. Про тур", "Russian River Cup", 'Mountain Bay Open', 'Чемпионат Восточной Европы', 'daily aqua tour', 'daily premier tour', 'daily pro tour']
useAPI = True
apiLiveIP = 'http://b-api.org/1x-api/live/Tennis/'

browser = webdriver.Firefox(log_path='NUL')



class OneXStavka(object):
    def __init__(self, browser, url, login, password, amount, apiLiveIP, useAPI, useAutoLogin):
        self.browser = browser
        self.login = login
        self.password = password
        self.url = url
        self.amount = amount
        self.apiLiveIP = apiLiveIP
        self.sleep30min = False
        self.useAPI = useAPI
        self.useAutoLogin = useAutoLogin

        self.individualTotalFirst = False
        self.individualTotalSecond = False
        self.individualTotalOne = False

        self.closeProgram = False

        try:
            file = open("buff.json", 'x')
            file.close()
        except FileExistsError:
            pass

        try:
            file = open("buffTelegram.json", 'x')
            file.close()
        except FileExistsError:
            pass

        try:
            file = open("OldInf.json", 'x')
            file.close()
        except FileExistsError:
            pass

        try:
            file = open("dublicates.json", 'x')
            file.close()
        except FileExistsError:
            pass

    def readInfo(self, file):
        with open(file, 'r') as file:
            try:
                oldInformation = json.load(file)
            except:
                oldInformation = {}
        return oldInformation

    def writeInfo(self, info, nameFile):
        with open(nameFile, 'w') as file:
            json.dump(info, file)

    def apiLive(self):
        return requests.get(self.apiLiveIP).json()

    def clearRamBrowser(self, browser):
        pid = browser.capabilities['moz:processID']
        proc_list = os.popen('tasklist /FO CSV').read()
        proc_list = proc_list.split('\n')[3:-1]
        procPidRam = {}
        for i in proc_list:
            try:
                procPidRam.update({int(i.replace('"', '').split(',')[1]): int(
                    ''.join([a for a in i.replace('"', '').split(',')[-1][:-3] if a.isdigit()]))})
            except:
                pass
        if procPidRam[pid] > 400000:
            browser.quit()

    def getIndividualTotal(self, browser, favorite: str):
        # Проверка на сеты
        countSets = browser.find_element_by_class_name('db-sport__bottom').text
        if [i for i in countSets if i.isdigit()][0] == '7':
            tries = 0
            while 1:
                try:
                    game = browser.find_element_by_class_name('main_game')
                    stavki = game.find_element_by_class_name('bets_content')
                    parties = stavki.find_elements_by_class_name('bet_group_col')
                    for stavki in parties:
                        stavki = stavki.find_elements_by_class_name('bet_group')
                        for stavka in stavki:
                            nameStavka = str(stavka.find_element_by_class_name('bet-title').text).strip()
                            if nameStavka == 'Индивидуальный тотал 2-го':
                                self.individualTotalSecond = stavka.find_element_by_class_name('bets')
                            if nameStavka == 'Индивидуальный тотал 1-го':
                                self.individualTotalFirst = stavka.find_element_by_class_name('bets')
                    tries = 0
                    break
                except common.exceptions.NoSuchElementException:
                    tries += 1
                    browser.refresh()
                    time.sleep(5)
                    ActionChains(self.browser).move_to_element(
                        self.browser.find_element_by_css_selector('#_logo')).perform()
                    ActionChains(self.browser).move_by_offset(5, 5).perform()
                    sleep(0.5)
                    if tries > 15:
                        return False


            try:
                self.individualTotalFirst = float(self.individualTotalFirst.text.split('\n')[0][:-2])
                self.individualTotalSecond = float(self.individualTotalSecond.text.split('\n')[0][:-2])
            except AttributeError:
                return False

            if favorite == '1':
                return self.individualTotalFirst, self.individualTotalSecond
            elif favorite == '2':
                return self.individualTotalSecond, self.individualTotalFirst

    def autoLogin(self):
        self.setMinimizeMemory()
        self.browser.get(self.url)
        ActionChains(browser).move_to_element(browser.find_element_by_css_selector('#_logo')).perform()
        sleep(0.5)
        browser.find_element_by_css_selector('.loginDropTop_con').click()
        sleep(1)
        browser.find_element_by_css_selector('#auth_id_email').send_keys(self.login)
        browser.find_element_by_css_selector('#auth-form-password').send_keys(self.password)
        sleep(2)
        browser.find_element_by_css_selector('#remember_user').click()
        sleep(1)
        browser.find_element_by_css_selector('.auth-button').click()
        sleep(5)

    def manualLogin(self):
        self.browser.get(url)
        print('Выбран ручной вход')
        print('Когда вы самостоятельно войдете в аккаунт нажмите Enter')
        input()

    def turnOnBetInOneClick(self):

        # betOnOneClick = self.browser.find_element_by_class_name('flex-grid')
        self.browser.find_element_by_css_selector('.c-spinner__input--small').send_keys(Keys.CONTROL + 'A')
        self.browser.find_element_by_css_selector('.c-spinner__input--small').send_keys(Keys.DELETE)
        self.browser.find_element_by_css_selector('.c-spinner__input--small').send_keys(self.amount)
        try:
            sleep(5)
            self.browser.find_element_by_css_selector("div.doublewin-question__button:nth-child(2)").click()
            sleep(3)
        except:
            pass
        self.browser.find_element_by_css_selector('.switch__label').click()
        sleep(3)
        self.browser.find_element_by_xpath("//button[contains(.,'ОК')]").click()
        sleep(1)

    def setMinimizeMemory(self):
        browser.get('about:memory')
        sleep(1)
        browser.find_element_by_css_selector('div.opsRow:nth-child(3) > button:nth-child(4)').click()
        sleep(1)

    def checkHistory(self, nameNewBet):
        print('name')
        print(nameNewBet)

        browser.execute_script("window.open('','_blank');")
        browser.switch_to.window(browser.window_handles[-1])
        self.browser.get(url + '/office/history/')
        sleep(5)

        names = []
        try:
            allBets = self.browser.find_elements_by_class_name('apm-panel')
            for bet in allBets:
                betBlockName = bet.find_element_by_class_name('apm-panel-head__block_name')
                name = betBlockName.find_element_by_class_name('apm-panel-head__text').text
                print(name)
                timeStr = bet.find_element_by_class_name('apm-panel-head__block').find_element_by_class_name('apm-panel-head__subtext').text
                timeStr = time.mktime(datetime.datetime.strptime(timeStr, 'от %d.%m.%Y | %H:%M').timetuple())
                if (time.time() - timeStr) < 1800:
                    names += [name]
            print('История ставок')
            print(names)
        except common.exceptions.NoSuchElementException:
            return True

        if len(browser.window_handles)> 2:
            while len(browser.window_handles) != 2:
                browser.close()
                browser.switch_to.window(browser.window_handles[-1])
                sleep(1)



        if len([x for x in names if names.count(x) > 1]) > 0:
            print('Были найдены дубликаты')
            sleep(1800)


        nameNewBet = nameNewBet.split('\n')[0]
        names = [i.split(' - ')[0] for i in names]
        print('История ставок')
        print('Имя')
        print(nameNewBet)
        print(names)
        print(nameNewBet in names)
        if nameNewBet in names:
            return True
        else:
            return False

    def historyBuffSync(self):
        p = 0
        while 1:
            names = []
            try:
                allBets = self.browser.find_elements_by_class_name('apm-panel')
                for bet in allBets:
                    betBlockName = bet.find_element_by_class_name('apm-panel-head__block_name')
                    name = betBlockName.find_element_by_class_name('apm-panel-head__text').text
                    print('История ставок имена:')
                    print(name)
                break
            except common.exceptions.NoSuchElementException:
                if p > 10:
                    return 'BAD'
                else:
                    p += 1

        if len(names) > 0:
            names = [i.replace(' - ', '\n') for i in names]
            buff = self.readInfo('buff.json')
            new = {}
            [new.update({i: buff[i]}) for i in buff.keys() if buff[i]['name'] in names]
            self.writeInfo(new, 'buff.json')

    def algoritm(self):
        self.browser.get(self.url + '/live/Tennis/')
        sleep(5)
        ActionChains(self.browser).move_to_element(self.browser.find_element_by_css_selector('#_logo')).perform()
        ActionChains(self.browser).move_by_offset(5, 5).perform()
        sleep(0.5)

        countForReloadPage = 0
        while 1:
            countForReloadPage += 1
            if countForReloadPage > 200:
                countForReloadPage = 0
                browser.refresh()
                time.sleep(5)
                ActionChains(self.browser).move_to_element(
                    self.browser.find_element_by_css_selector('#_logo')).perform()
                ActionChains(self.browser).move_by_offset(5, 5).perform()
                sleep(0.5)

            try:
                games = browser.find_element_by_id('games_content').find_element_by_xpath('div/div/div[1]')
                games = games.find_elements_by_xpath('div')

                for game in games:
                    try:
                        game = game.find_elements_by_xpath('div')
                    except common.exceptions.StaleElementReferenceException:
                        continue

                    liga = game[0].text.split('\n')[0]

                    #Отсев лишних лиг
                    # if liga.lower().find('женщины') != -1:
                    #     continue



                    if True in [True for delLig in delLigs if liga.lower().strip().find(delLig) != -1]:
                        continue

                    oldURLS = self.readInfo('buff.json')
                    oldURLS = list(oldURLS.values())
                    oldURLS = [i['url'] for i in oldURLS]

                    matches = game[1:]
                    for match in matches:
                        try:
                            name = match.find_element_by_class_name('c-events__name').text
                            while name.find('(') != -1:
                                name = name[:name.find('(')] + name[name.find(')') + 1:]
                            # print(name)
                            name = name.split('\n')
                            name = [i.strip() for i in name]
                            name = '\n'.join(name)

                            url = match.find_element_by_class_name('c-events__name').get_attribute('href')
                            if url in oldURLS:
                                continue

                            try:
                                total = match.find_elements_by_class_name('c-bets__bet')[4].text
                            except IndexError:
                                continue
                            if total == '-':
                                continue

                        except common.exceptions.StaleElementReferenceException:
                            continue

                        if self.useAPI:
                            try:
                                oldFirstKoef = float(self.apiLive()[liga][name]['firstKoef'])
                                oldSecondKoef = float(self.apiLive()[liga][name]['secondKoef'])
                                oldTotal = float(self.apiLive()[liga][name]['total'])
                            except (KeyError, ValueError):
                                continue
                            except requests.exceptions.ConnectionError:
                                print('Ошибка соединения с API')
                                continue
                        else:
                            try:
                                oldFirstKoef = float(self.readInfo("lineTennis.json")[liga][name]['firstKoef'])
                                oldSecondKoef = float(self.readInfo("lineTennis.json")[liga][name]['secondKoef'])
                                oldTotal = float(self.readInfo("lineTennis.json")[liga][name]['total'])
                            except (KeyError, ValueError):
                                continue

                        if oldFirstKoef <= oldSecondKoef:
                            favoriteNumber = "1"
                            favorite = oldFirstKoef
                            outsider = oldSecondKoef
                        else:
                            favoriteNumber = "2"
                            favorite = oldSecondKoef
                            outsider = oldFirstKoef

                        print(liga)
                        print(name)
                        print(total)
                        print('Фаворит коэф', favorite)
                        print('Разница тоталов', (float(total) - float(oldTotal)))
                        print(url)
                        print('\n\n')

                        if float(favorite) <= 1.6:

                            if float(total) >= 24.5:

                                if (float(total) - float(oldTotal)) >= 8:
                                    # После добавления в буффер нужно пропускать проверку individualTotal


                                    print(liga)
                                    print(name)
                                    print(total)
                                    print(url)
                                    print('\n\n')


                                    self.placeBet(url, match.find_elements_by_class_name('c-bets__bet')[5], name)
                                        # Тут мы нашли подходящий матч
                                        # Ставим на больший из коэффициентов ИНДИВИДУАЛЬНЫЙ ТОТАЛ меньше

                                    try:
                                        browser.find_element_by_css_selector(".c-btn--size-m").click()
                                    except:
                                        pass
                                    while len(browser.window_handles) != 1:
                                        browser.close()
                                        browser.switch_to.window(browser.window_handles[-1])
                                    try:
                                        browser.find_element_by_css_selector(".c-btn--size-m").click()
                                    except:
                                        pass

                if self.useAutoLogin:
                    self.clearRamBrowser(browser)


            except (exceptions.ProtocolError, common.exceptions.NoSuchElementException, common.exceptions.StaleElementReferenceException):
                while len(browser.window_handles) != 1:
                    browser.close()
                    browser.switch_to.window(browser.window_handles[-1])
                browser.refresh()
                time.sleep(5)
                ActionChains(self.browser).move_to_element(
                    self.browser.find_element_by_css_selector('#_logo')).perform()
                ActionChains(self.browser).move_by_offset(5, 5).perform()
                sleep(0.5)

    def buffAnalys(self, url, name):
        data = self.readInfo('buff.json')
        dataTwo = self.readInfo('buff.json')

        [dataTwo.pop(i) for i in data.keys() if (float(i) + 7200) < time.time()]

        oldUrls = [i['url'] for i in dataTwo.values()]
        oldNames = [i['name'] for i in dataTwo.values()]


        if (url in oldUrls) or (name in oldNames):
            status = False
        else:
            dataTwo[time.time()] = {'url': url, 'name': name}
            status = True

        self.writeInfo(dataTwo, 'buff.json')
        return status

    def dublicateAnalys(self):
        data = self.readInfo('dublicates.json')
        dataTwo = self.readInfo('dublicates.json')

        [dataTwo.pop(i) for i in data.keys() if (float(i) + 10800) < time.time()]

        self.writeInfo(dataTwo, 'dublicates.json')

    def placeBet(self, url, element, name):
        winsound.Beep(200, 1000)

        tries = 0
        while 1:
            try:

                desired_y = (element.size['height'] / 2) + element.location['y']
                window_h = browser.execute_script('return window.innerHeight')
                window_y = browser.execute_script('return window.pageYOffset')
                current_y = (window_h / 2) + window_y
                scroll_y_by = desired_y - current_y

                browser.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)

                ActionChains(browser).move_to_element(element).perform()
                sleep(0.5)
                p = 0
                tries = 0
                flag = 'again'

                while 1:
                    try:
                        if flag == True:
                            break
                        elif flag == 'BAD':
                            break
                        elif flag == 'VERY BAD':
                            1 / 0

                        if flag == 'again':
                            try:
                                element.click()
                                sleep(0.5)
                                element.click()
                                sleep(0.5)
                                element.click()
                                sleep(10)
                                flag = ''
                                break
                            except common.exceptions.ElementClickInterceptedException:
                                print('Не удалось поставить. Ставка загорожена. Попытка закрыть окно')
                                flag = ''


                        while 1:
                            try:
                                if self.browser.find_element_by_css_selector('#swal2-title').text == 'Ошибка':
                                    sleep(0.5)
                                    self.browser.find_element_by_css_selector('.swal2-confirm').click()
                                    print('Окно с ошибкой при ставке')
                                    if p > 15:

                                        flag = 'BAD'
                                        break
                                    else:
                                        p += 1
                                        flag = 'again'
                                        break
                                        # return to click
                            except common.exceptions.NoSuchElementException:
                                pass

                            try:
                                browser.find_element_by_css_selector(".c-btn--size-m").click()
                                print('Нашли кнопку')
                                sleep(3)
                                flag = True
                                break
                            except common.exceptions.NoSuchElementException:
                                flag = ''


                        if tries > 60:
                            flag = 'BAD'
                            print('Время ожидания ставки истекло')
                        else:
                            tries += 1
                            sleep(1)


                    except common.exceptions.ElementClickInterceptedException:
                        print('Не удалось поставить. Ставка заблокирована или чем-то загорожена')
                        flag = 'VERY BAD'

                try:
                    browser.find_element_by_css_selector(".c-btn--size-m").click()
                except:
                    pass

                try:
                    browser.find_element_by_css_selector(".c-btn--size-m").click()
                except:
                    pass

                sleep(5)

                try:
                    browser.find_element_by_css_selector(".c-btn--size-m").click()
                except:
                    pass

                try:
                    browser.find_element_by_css_selector(".c-btn--size-m").click()
                except:
                    pass
                sleep(5)
                if self.checkHistory(name):
                    self.buffAnalys(url, name)

                self.historyBuffSync()

                try:
                    browser.find_element_by_css_selector(".c-btn--size-m").click()
                except:
                    pass
                try:
                    browser.find_element_by_css_selector(".c-btn--size-m").click()
                except:
                    pass

                tries = 0
                break
            except common.exceptions.NoSuchElementException:
                tries += 1
                browser.refresh()
                time.sleep(5)
                ActionChains(self.browser).move_to_element(
                    self.browser.find_element_by_css_selector('#_logo')).perform()
                ActionChains(self.browser).move_by_offset(5, 5).perform()
                sleep(0.5)
                if tries > 10:
                    print('BAD')
                    1/0


controlPanel = OneXStavka(browser, url, login, password, amount, apiLiveIP, useAPI, autoLogin)

while 1:
    try:
        if autoLogin:
            controlPanel.autoLogin()
        else:
            controlPanel.manualLogin()
        controlPanel.turnOnBetInOneClick()
        controlPanel.algoritm()
    except:
         print('Полный перезапуск автоставки')
         try:
             browser.quit()
             browser.quit()
         except:
             pass
         browser = webdriver.Firefox(log_path='NUL')
         print('Запуск браузера')
         controlPanel = OneXStavka(browser, url, login, password, amount, apiLiveIP, useAPI, autoLogin)
