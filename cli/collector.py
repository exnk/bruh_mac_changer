import typer
from utils.get_contact import ContactParse
from utils.recon import Recon


app = typer.Typer()


@app.command()
def get_contacts(host: str = typer.Argument(..., help='Название интерфейса на котором нужно выполнить замену'),
                 mods: str = typer.Option(default=['recon'])):
    if ',' in mods:
        mods = mods.split(',')
    if 'recon' in mods:
        print('Run base recon')
        Recon(host).run()
    if 'contact' in mods:
        print('run contact parse')
        ContactParse(host).run_walk()
    print('Парсинг закончили, см папку Result')
