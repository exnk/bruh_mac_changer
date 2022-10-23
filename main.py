import sys

import typer
import os
from typing import Union

from utils.ifc_module import IFConfig
from models.ifconfig_models import Ifmodel
import json
import yaml
from rich.pretty import pprint


app = typer.Typer()
lens = os.popen('ifconfig -l').read().split()


def interface_callback(interface: str) -> Union[bool, str]:
    if interface in lens or interface == 'all':
        return interface
    return False


def format_callback(fmt: str) -> Union[bool, str]:
    tmp_fmt = fmt
    if '/' in tmp_fmt or '\\' in tmp_fmt:
        return False
    if '.' in tmp_fmt:
        tmp_fmt = tmp_fmt.rsplit('.', 1)[-1]
    valid_formats = ('json', 'yaml', 'txt', '')
    return fmt if tmp_fmt in valid_formats else False


def write_output(data: Union[Ifmodel, dict[Ifmodel]], fmt: str, name: str = 'output') -> None:
    if isinstance(data, dict):
        data = {k: v.dict(exclude_none=True) for k, v in data.items()}
    with open(f'./{name}.{fmt}', 'w') as out_file:
        if fmt == 'json':
            json.dump(data, out_file, indent=4)
        elif fmt == 'yaml':
            yaml.dump(data, out_file)
        else:
            out_file.write(json.dumps(data, indent=4))


@app.command()
def truncate_table(): ...


@app.command()
def restore(): ...


@app.command()
def change(): ...


@app.command()
def get_info(interface: str = typer.Option(default='all',
                                           callback=interface_callback),
             output: str = typer.Option(default='',
                                        callback=format_callback)
             ) -> None:
    data = IFConfig(os.popen('ifconfig -a').read())
    sys.stdout.write(f'Обработка interface {interface} | Output {output if output != "" else "console"}')
    if interface != 'all':
        data = data.interface(interface=interface).__repr__()
    else:
        data = data.__repr__()
    sys.stdout.write('\nВывод данных\n')
    if output:
        if '.' in output:
            output = output.rsplit('.', 1)
            write_output(data=data,
                         fmt=output[1],
                         name=output[0]
                         )
        else:
            write_output(data=data,
                         fmt=output
                         )
    else:
        pprint(data)


if __name__ == '__main__':
    app()
