import re
import typer
from utils.page_parser import ContactParse
from utils.recon import Recon
from requests import get


app = typer.Typer()


recon_help = """
Моды которые нужно применить при вызове. На данный момент доступны: \ncontacs- граб мейлов и телефонов
\nrecon - сбор инфы по хосту
моды можно передавать через ',' """

@app.command()
def get_contacts(host: str = typer.Argument(..., help='Название хоста который хотим пройти'),
                 mods: str = typer.Option(default=['contact'], help=recon_help),
                 wordlist: str = typer.Option(default=None,
                                              help='список словарей по которым надо пройтись в рамках путей'),
                 autowalk: bool = typer.Option(default=False, is_flag=True,
                                               help="будем ли автоматом собирать и идти по найденым страницам"),
                 subcheck: bool = typer.Option(default=False, is_flag=True,
                                               help="флаг для мода recon. будем ли проверять доступность субдоменов")):
    def normalize_link(link: str):
        if 'www' in link:
            link = link.replace('www.', '')
        if not link.endswith('/'):
            link = link + '/'
        if not link.startswith('http://') and not link.startswith('https://'):
            proto = typer.prompt('What to use? http:// or https://. Input it')
            if '://' in proto:
                return f'{proto}{link}'
            else:
                return f'{proto}://{link}'
        return link
    host = normalize_link(host)
    print(host)
    if ',' in mods:
        mods = mods.split(',')
    if 'recon' in mods:
        print('Run base recon')
        Recon(host, subcheck).run()
    if 'contact' in mods:
        print('run contact parse')
        ContactParse(host, wordlist=wordlist, autowalk=autowalk).run_walk()
    print('Парсинг закончили, см папку Result')
