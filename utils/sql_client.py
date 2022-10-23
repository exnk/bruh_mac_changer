import sqlite3

from typing import Union


class SQLClient:

    def __init__(self, db_name: str) -> None:
        self.__conn = sqlite3.connect(db_name)
        self.cursor = self.__conn.cursor()

    def select_from_vendor(self,
                           vendor_name: str = None,
                           vendor_mask: str = None
                           ) -> list:
        if vendor_mask and ':' in vendor_mask:
            vendor_mask = vendor_mask.replace(':', '')

        name = '' if vendor_name is None else f"name like '{vendor_name}%'"
        mask = '' if vendor_mask is None else f"mac_prefix like '{vendor_mask}%'"

        if name != '' and mask != '':
            name = ' '.join([name, 'and', mask])
        elif mask != '':
            name = mask

        query = f"""
        SELECT name, mac_prefix from vendors where {name}
        """

        return self.cursor.execute(query).fetchall()

    def get_vendors(self) -> list:
        query = """select name from vendors group by name"""
        return self.cursor.execute(query).fetchall()

    def get_stored_info(self, interface: str = None) -> Union[list, str]:
        if interface:
            query = f"""select * from restore_data where interface like '{interface}%'"""
            result = self.cursor.execute(query).fetchall()
            return result if len(result) == 0 else result[0]
        else:
            query = """select * from restore_data"""
            return self.cursor.execute(query).fetchall()

    def store_interface(self, interface: str, value: str) -> bool:
        if not self.get_stored_info(interface=interface):
            query = f"""insert into restore_data (interface, value) values ('{interface}','{value}')"""
            self.cursor.executescript(query)
            assert self.get_stored_info(interface=interface) == (interface, value)
        return True

    def write_log(self, interface: str, old_value: str, new_value: str) -> None:
        query = f"""insert into change_log (interface, old_value, new_value) 
        values ('{interface}','{old_value}', '{new_value}')"""
        self.cursor.executescript(query)

    def truncate_data(self):
        tables = ('change_log', 'restore_data')
        query = """delete from {} """
        for table in tables:
            self.cursor.execute(query.format(table))

