import re

import warnings
from os import listdir
from string import digits
from time import sleep
from os.path import exists
from requests import Session

from selenium import webdriver
from selenium.webdriver.common.by import By

warnings.filterwarnings("ignore")


js_error = 'this site requires javascript to be enabled'


class ContactParse:
    walked_list = []
    phone_re = '[+]*[ ]*[0-9]*[ ]*[(]{0,1}[0-9]{1,4}[)][ ]*[[0-9]{1,4}]*[ ]*[-]*[[0-9]{1,3}]*[ ]*[-]*[[0-9]{1,3}]*'
    mails_re = r'[\w.+-]+@[\w-]+\.[\w.-]+'
    href_re = 'href=(["\'])(.*?)\\1'
    __black_list = ('.jpg', '.png', '.gif', '.css', '.js', '.ico')
    phones = []
    mails = []
    names = []
    bad_list = []

    def __init__(self,
                 url: str,
                 timeout: int = 1,
                 wordlist: str | None = False,
                 autowalk: bool = True) -> None:
        self.url = url
        self.client = Session()
        self.client.verify = False
        self.ui_client: webdriver.Chrome | None = None
        self.timeout = timeout
        self.walk_list = []
        self._autorun = False
        if wordlist:
            if exists(wordlist):
                with open(wordlist, 'r', encoding='utf-8') as wl:
                    self.walk_list.extend(wl.readlines())
            else:
                if wordlist in listdir('./data/wordlists/'):
                    with open('./data/wordlists/' + wordlist, 'r', encoding='utf-8') as wl:
                        self.walk_list.extend(wl.readlines())
        self.__ui = False
        self.__autowalk = autowalk

    def _walk_init(self):
        req = self.client.get(self.url)
        self.walk_list.insert(0, '/')
        if js_error in req.text:
            self.__ui = True
            self.client = webdriver.Chrome(executable_path='tools/chromedriver')

    def walk_urls_update(self, urls: list):
        res = []
        for href in urls:
            if not href.startswith('/') and self.url not in href:
                continue
            href = href.replace(self.url, '')
            if href in self.walked_list or href in self.walk_list:
                continue
            if href == '/' or href == '':
                continue
            if any(True if black in href else False for black in self.__black_list):
                continue
            self.walk_list.append(href)
            res.append(href)
        return res

    @staticmethod
    def __update_lists(upd_list: list, core_list: list):
        def normalize(value: str):
            if any(True if sign in value else False for sign in '+-()') \
               and len(list(filter(lambda x: x in digits, list(value)))) > 4:
                return value.replace('+', '').replace('-', '').replace(' ', '')
            elif all(True if sign in value else False for sign in '@.') and len(value.split('@')) == 2:
                return value.replace('mailto:')
            else:
                return value
        for item in upd_list:
            p = normalize(item)
            if p in core_list:
                continue
            core_list.append(p)

    def collector(self, raw, reg, lst):
        res_list = list(re.findall(reg, raw))
        self.__update_lists(res_list, lst)

    def auto_walker(self, request: callable):

        while len(self.walk_list) > 0:
            page = self.walk_list.pop(0)
            print(f'[+] Current page {page}')
            self.walked_list.append(page)
            res = request(page)
            hrefs = [href[-1] for href in list(re.findall(self.href_re, res))]
            self.collector(res, self.mails_re, self.mails)
            self.collector(res, self.phone_re, self.phones)
            self.walk_urls_update(hrefs)
            sleep(self.timeout)

    def manual_walker(self, request: callable):
        for page in self.walk_list:
            print(f'[+] Current page {page}')
            res = request(page)
            self.walked_list.append(page)
            self.collector(res, self.mails_re, self.mails)
            self.collector(res, self.phone_re, self.phones)
            sleep(self.timeout)

    def run_walker(self):
        def selene_request(page):
            self.client.get(self.url + page)
            return self.client.find_element(By.CSS_SELECTOR, 'html').get_attribute('innerHTML')

        def req_request(page) -> str:
            res = self.client.get(self.url + page)
            if res.status_code > 400:
                print(f'[-] Страница {page} вернула 404')
                self.bad_list.append(page)
            return res.text

        request_ = selene_request if self.__ui else req_request

        if self.__autowalk:
            self.auto_walker(request_)
        else:
            self.manual_walker(request_)

    def run_walk(self):
        self._walk_init()
        self.run_walker()

        with open('./result/phones.txt', 'w') as ph:
            ph.writelines([f'{line}\n' for line in self.phones])

        with open('./result/mails.txt', 'w') as ml:
            ml.writelines(self.mails)

        with open('./result/pages', 'w') as pg:
            pg.writelines(self.walked_list)
