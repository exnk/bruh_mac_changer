from time import sleep
from requests import Session
from requests.exceptions import ReadTimeout, ConnectionError
from json import dumps
from models.recon_models import Host, Cert, Subdomain, Address, MX


class Recon:
    whois_key = '957fd9f5ce71c80d5250ba17f5dfbc3e'

    def __init__(self, url, check_subdomains: bool = False):
        self.session = Session()
        self.session.verify = False
        self.url = self.__normalize_url(url)
        self.model = Host(url=self.url)
        self.check_sub = check_subdomains

    @staticmethod
    def __normalize_url(url):
        if '//' in url:
            url = url.split('//')[-1]
        return url.replace('wwww.', '')

    def bevigil(self):
        headers = {'X-Access-Token': '8VV4UlOsG1b462cm'}
        res = self.session.get(
            f'https://osint.bevigil.com/api/{self.url}/subdomains/',
            headers=headers)
        return res.json()

    def threat(self):
        """Not work now Deprecated?"""
        params = {'q': self.url, 'rt': 5}
        self.session.get('https://api.threatminer.org/v2/domain.php', params=params)

    def cert(self):
        """TODO"""
        url = 'https://api.certspotter.com/v1/issuances'
        cs_params = {
            'domain': self.url,
            'expand': 'dns_names',
            'include_subdomains': 'true'
        }
        res = self.session.get(url, params=cs_params).json()
        for cert in res:
            self.model.certs.append(Cert(**cert))

    def htarget(self):
        """TODO"""
        url = f'https://api.hackertarget.com/hostsearch/?q={self.url}'
        res = self.session.get(url).text.split('\n')
        for item in res:
            tmp = item.split(',')
            try:
                self.model.subdomains.append(Subdomain(url=tmp[0], ip=tmp[1]))
            except IndexError: pass

    def dns_recon(self):
        headers = {'x-api-key': '53681419-4ce1-4132-85ac-10310ef7d642', 'Content-Type': 'application/json'}
        url = f'https://api.geekflare.com/dnsrecord'
        data = {"url": f"https://{self.url}"}
        res = self.session.post(url, data=dumps(data), headers=headers).json()['data']

        for item in res['A']:
            self.model.A.append(Address(**item))
        for item in res['MX']:
            self.model.mx.append(MX(**item))
        self.model.NS = res['NS']
        return res

    def check_subdomains(self):
        print('Start subdomains availability check')
        for item in self.model.subdomains:
            domain = item.url
            domains = []
            if 'http:' in domain:
                domains.append(domain)
                domains.append(domain.replace('http', 'https'))
            elif 'https' in domain:
                domains.append(domain)
                domains.append(domain.replace('https', 'http'))
            else:
                domains.append(f'http://{domain}')
                domains.append(f'https://{domain}')
            for dm in domains:
                try:
                    self.session.get(dm, timeout=1)
                    print(f'--[+] domain {dm} avaliable')
                except (ReadTimeout, ConnectionError):
                    print(f'--[-] domain {dm} unavaliable')
                sleep(0.5)

    def run(self):

        self.dns_recon()
        print('[X] DNS Checked')
        self.htarget()
        print('[X] Data Checked')
        self.cert()
        print('[X] Cert Checked')
        if self.check_sub:
            self.check_subdomains()
        with open('./result/rec.json', 'w') as js:
            js.write(self.model.json())
        print('[+] Recon done. Output result/rec.json')
