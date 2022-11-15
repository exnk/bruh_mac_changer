import time
import warnings

from requests import Session
import re

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

    def __init__(self,
                 url: str,
                 timeout: int = 2,
                 ui: bool = False,
                 wordlist: bool = False) -> None:
        self.url = url
        self.api_client = Session()
        self.ui = ui
        self.api_client.verify = False
        self.ui_client: webdriver.Chrome | None = None
        self.timeout = timeout
        self.walk_path_list: list | None | bool = wordlist
        self._autorun = False

    def _walk_init(self):
        req = self.api_client.get(self.url)
        if self.walk_path_list is True:
            with open('data/wordlists/contacts', 'r') as file:
                self.walk_path_list = file.readlines()
        elif self.walk_path_list is False:
            self.walk_path_list = []
            self._autorun = True
            self.walk_path_list.append('')
        elif isinstance(self.walk_path_list, str):
            with open(self.walk_path_list) as file:
                self.walk_path_list = file.readlines()
        if js_error in req.text:
            self.ui = True
            self.ui_client = webdriver.Chrome(executable_path='tools/chromedriver')

    @staticmethod
    def normalize(phone: str):
        if isinstance(phone, str):
            return phone.replace('+', '').replace('-', '').replace(' ', '')
        else:
            return phone

    def __update_lists(self, upd_list: list, core_list: list):
        for item in upd_list:
            p = self.normalize(item)
            if p in core_list:
                continue
            core_list.append(p)

    def collector(self, raw, reg, lst):
        res_list = list(re.findall(reg, raw))
        self.__update_lists(res_list, lst)

    def _autorun_list(self, raw):
        if self._autorun:
            phones = []
            mail = []
            hrefs = [href[-1] for href in list(re.findall(self.href_re, raw))]
            for href in hrefs:
                if href in self.walked_list or href in self.walk_path_list:

                    continue
                if any(True if part in href else False for part in self.__black_list):
                    continue
                if href.startswith('/'):
                    self.walk_path_list.append(href)
                    continue
                if href.replace(self.url, '') in self.walked_list \
                        or self.url not in href \
                        or self.url == href:
                    continue

                if 'tel:' in href:
                    phones.append(href.replace('tel:', '').replace('%', ''))
                if 'mailto' in href:
                    mail.append(href.replace('mailto:', ''))
                hr = href[-1].replace(self.url, '')

                if hr in self.walk_path_list or hr in self.walked_list:
                    continue
                self.walk_path_list.append(hr)
            self.__update_lists(phones, self.phones)
            self.__update_lists(mail, self.mails)

    def request_walker(self):
        while len(self.walk_path_list) > 0:
            sub = self.walk_path_list.pop(0)
            print(f'current page {sub}')
            if sub in self.walked_list:
                continue
            self.walked_list.append(sub)
            url = self.url + sub
            res = self.api_client.get(url).text
            self.collector(res, self.phone_re, self.phones)
            self.collector(res, self.mails_re, self.mails)
            self._autorun_list(res)
            time.sleep(self.timeout)

    def selene_walker(self):
        while len(self.walk_path_list) > 0:
            sub = self.walk_path_list.pop(0)
            self.walked_list.append(sub)
            url = self.url + sub
            self.ui_client.get(url)
            time.sleep(self.timeout)
            res = self.ui_client.find_element(By.CSS_SELECTOR, 'html').get_attribute('innerHTML')
            self.collector(res, self.phone_re, self.phones)
            self.collector(res, self.mails_re, self.mails)
            self._autorun_list(res)

    def run_walk(self):
        self._walk_init()
        if self.ui_client:
            self.selene_walker()
        else:
            print('start walking')
            self.request_walker()
        with open('./result/phones.txt', 'w') as ph:
            ph.writelines(self.phones)
        with open('./result/mails.txt', 'w') as ml:
            ml.writelines(self.mails)
        with open('./result/pages', 'w') as pg:
            pg.writelines(self.walked_list)
