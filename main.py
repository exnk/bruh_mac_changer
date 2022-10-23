import os
import sys
import json

import yaml
import typer

from typing import Union
from rich.pretty import pprint

from utils.ifc_module import IFConfig
from utils.sql_client import SQLClient
from models.ifconfig_models import Ifmodel
from utils.helper import generate_mac, get_vendor_mask, choice_random_vendor_mask


app = typer.Typer()
lens = os.popen('ifconfig -l').read().split()
__db_cli = SQLClient('identifier.sqlite')


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
def show_logs():
    print('Упс, а тут пустая заглушка')


@app.command()
def truncate_table():
    ask = typer.prompt('Вы действительно хотите отчистить таблицы? [Y/N]',
                       confirmation_prompt=True)
    if ask in ['Y', 'yes', 'y', 'YES']:
        __db_cli.truncate_data()
    else:
        print('Удаления нет, но вы держитесь :3\nПо крайней мере, Вы пытались')


@app.command()
def restore():
    data_for_restore = __db_cli.get_stored_info()
    data = IFConfig(os.popen('ifconfig -a').read())
    interfaces = data.__repr__().keys()
    restored = []
    for item in data_for_restore:
        if item[0] in interfaces and item[1] != data.interface(item[0])['mac']:
            interface = data.interface(item[0])
            interface.change_mac(mac=item[1],
                                 restore=True)
            restored.append(interface['name'])
    print(f'Восстановлены значения у {restored}')


@app.command(help='Изменение MAC адреса на интерфейсе')
def change(interface: str = typer.Argument(..., callback=interface_callback),
           vendor: str = typer.Option(default='random'),
           mac: str = typer.Option(default='')
           ):
    iface = IFConfig(os.popen(f'ifconfig {interface}').read()).interface(interface=interface)
    if vendor and vendor != 'random':
        data = get_vendor_mask(vendor)[1]
    elif mac:
        data = mac
    else:
        data = choice_random_vendor_mask()[1]
    mac = generate_mac(data)
    iface.change_mac(mac)


@app.command()
def get_info(interface: str = typer.Option(default='all',
                                           callback=interface_callback),
             output: str = typer.Option(default='',
                                        callback=format_callback),
             show_mac: bool = typer.Option(default=False,
                                           is_flag=True)
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
        if show_mac:
            if isinstance(data, Ifmodel):
                data = f'{data.name} : {data.mac}'
            else:
                data = '\n'.join([f'{v.name} : {v.mac} ' for k, v in data.items()])
            print(data)
        else:
            pprint(data)


if __name__ == '__main__':
    app()
