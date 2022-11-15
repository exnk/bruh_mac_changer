from requests import Session
from json import dumps


class Recon:
    whois_key = '957fd9f5ce71c80d5250ba17f5dfbc3e'

    def __init__(self, url):
        self.session = Session()
        self.session.verify = False
        self.url = self.__normalize_url(url)

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
        print(res.json())

    def threat(self):
        params = {'q': self.url, 'rt': 5}
        res = self.session.get('https://api.threatminer.org/v2/domain.php', params=params)
        print(res.json())

    def cert(self):
        url = 'https://api.certspotter.com/v1/issuances'
        cs_params = {
            'domain': self.url,
            'expand': 'dns_names',
            'include_subdomains': 'true'
        }
        res = self.session.get(url, params=cs_params)
        return res.json()

    def htarget(self):
        url = f'https://api.hackertarget.com/hostsearch/?q={self.url}'
        res = self.session.get(url)

        return res.text

    def dns_recon(self):
        headers = {'x-api-key': '53681419-4ce1-4132-85ac-10310ef7d642', 'Content-Type': 'application/json'}
        url = f'https://api.geekflare.com/dnsrecord'
        data = {"url": f"https://{self.url}"}
        res = self.session.post(url, data=dumps(data), headers=headers)
        return res.json()


    def run(self):
        data = {
            'dns_lookup': self.dns_recon(),
            'htarget': self.htarget().split('\n'),
            'cert': self.cert()
        }
        with open('./result/rec.json', 'w') as js:
            js.write(dumps(data, indent=4))