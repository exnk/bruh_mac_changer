import os
import sys
import copy
import subprocess

from typing import Union

from jc import parse

from utils.sql_client import SQLClient
from models.ifconfig_models import Ifmodel


def normalize_to_models(raw: str,
                        client: SQLClient,
                        model: bool = False,
                        ) -> Union[dict, Ifmodel]:
    data: list[dict] = parse('ifconfig', raw)
    result: dict[str, Interface] = {}
    for item in data:
        res = copy.deepcopy(item)
        tx = {k: res.pop(k) for k, v in item.items() if 'tx' in k}
        rx = {k: res.pop(k) for k, v in item.items() if 'rx' in k}
        ip4 = {k: res.pop(k) for k, v in item.items() if 'ipv4' in k}
        ip6 = {k: res.pop(k) for k, v in item.items() if 'ipv6' in k}
        res.update(dict(
            tx=tx,
            rx=rx,
            ip4=ip4,
            ip6=ip6
        ))
        model_ = Ifmodel(**res)
        interface = Interface(model_, client)
        result.update({model_.name: interface})

    if model and len(result) == 1:
        return result[list(result.keys())[0]].__repr__()
    return result


class Interface:

    def __init__(self, interface_model: Ifmodel, sql: SQLClient) -> None:
        self.__client = sql
        self.__model = interface_model

    def __str__(self):
        return self.__model

    def __repr__(self):
        return self.__model

    def __getitem__(self, item):
        return self.__model.__getattribute__(item)

    def __store_data(self):
        self.__client.store_interface(interface=self.__model.name,
                                      value=self.__model.mac)

    def __write_log(self, old_mac: str):
        self.__client.write_log(interface=self.__model.name,
                                old_value=old_mac,
                                new_value=self.__model.mac)

    def _get_old_data(self):
        return self.__client.get_stored_info(self.__model.name)

    def change_mac(self, mac: str = None, restore: bool = False) -> None:
        if restore:
            old_data = self._get_old_data()
            mac = old_data[1]
            if mac == self.__model.mac:
                sys.stdout.write('Нельзя поменять стандартное значение на стандартное')
                return None
        self.__store_data()
        old_mac = self.__model.mac
        subprocess.call(f'ifconfig {self.__model.name} down', shell=True)
        subprocess.call(f'ifconfig {self.__model.name} hw ether {mac}', shell=True)
        subprocess.call(f'ifconfig {self.__model.name} up', shell=True)
        data = os.popen(f'ifconfig {self.__model.name}').read()
        result = normalize_to_models(data, self.__client, model=True)
        self.__model.mac = result.mac
        assert self.__model.mac != old_mac
        self.__write_log(old_mac=old_mac)
