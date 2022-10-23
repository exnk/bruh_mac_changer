import sqlite3


class SQLClient:

    def __init__(self, db_name: str) -> None:
        self.__conn = sqlite3.connect(db_name)
        self.cursor = self.__conn.cursor()

    def select_from_vendor(self,
                           vendor_name=None,
                           vendor_mask=None
                           ):

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

    def get_vendors(self):
        query = """
        select name from vendors group by name"""

        return self.cursor.execute(query).fetchall()
