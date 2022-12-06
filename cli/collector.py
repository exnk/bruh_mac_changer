import typer
from utils.page_parser import ContactParse
from utils.recon import Recon


app = typer.Typer()


@app.command()
def get_contacts(host: str = typer.Argument(..., help='Название хоста который хотим пройти'),
                 mods: str = typer.Option(default=['recon']),
                 wordlist: str = typer.Option(default=None),
                 autowalk: bool = typer.Option(default=False, is_flag=True),
                 subcheck: bool = typer.Option(default=False, is_flag=True)):
    if ',' in mods:
        mods = mods.split(',')
    if 'recon' in mods:
        print('Run base recon')
        Recon(host, subcheck).run()
    if 'contact' in mods:
        print('run contact parse')
        ContactParse(host, wordlist=wordlist, autowalk=autowalk).run_walk()
    print('Парсинг закончили, см папку Result')
