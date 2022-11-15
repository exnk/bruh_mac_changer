import typer
import cli.mac_changer as changer
import cli.collector as collect

app = typer.Typer()
app.add_typer(changer.app, name='macchanger')
app.add_typer(collect.app, name='collect')


if __name__ == '__main__':
    app()
