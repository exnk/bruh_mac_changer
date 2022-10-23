from models.ifconfig_models import Ifmodel
from utils.sql_client import SQLClient


class Interface:

    def __init__(self, interface_model: Ifmodel):
        self.__model = interface_model

    def __str__(self):
        return self.__model

    def __repr__(self):
        return self.__model

    def __store_data(self):
        client = SQLClient('./identifier.sqlite')
        client.store_interface(interface=self.__model.name,
                               value=self.__model.mac)
    def change_mac(self, mac: str, restore: bool = False): ...

