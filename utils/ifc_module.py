import sys

from utils.sql_client import SQLClient
from utils.interfaces import Interface, normalize_to_models


class IFConfig:

    def __init__(self,
                 raw: str
                 ) -> None:
        self.__sql: SQLClient = SQLClient('./identifier.sqlite')
        self.__raw: dict[str, Interface] = normalize_to_models(raw, self.__sql)

    def __str__(self) -> dict:
        return {k: v.__repr__() for k, v in self.__raw.items()}

    def __repr__(self) -> dict:
        return {k: v.__repr__() for k, v in self.__raw.items()}

    def __getitem__(self, item) -> Interface:
        return self.__raw[item]

    def interface(self,
                  interface: str
                  ) -> Interface:
        try:
            assert interface in self.__raw
        except AssertionError:
            sys.stdout.write(f"Error! Interface {interface} invalid!\nValid choices are% {' '.join(self.__raw)}")
        else:
            return self.__raw[interface]
