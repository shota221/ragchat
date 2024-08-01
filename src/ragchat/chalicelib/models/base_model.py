from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from injector import Injector
from chalicelib.clients.db_client import DBClient

class BaseModel(ABC):
    @classmethod
    @abstractmethod
    def table_name(cls):
        pass

    @classmethod
    @abstractmethod
    def primary_key_name(cls):
        pass

    def save(self):
        dict_data = asdict(self)
        item = self.as_item(dict_data)
        table_name = self.table_name()
        return Injector().get(DBClient).put_item(table_name, item)
    
    def delete(self):
        data_type = None
        if isinstance(getattr(self, self.primary_key_name()), str):
            data_type = "S"
        elif isinstance(getattr(self, self.primary_key_name()), int):
            data_type = "N"

        key = {
            self.primary_key_name(): {
                data_type: str(getattr(self, self.primary_key_name()))
            }
               }
        table_name = self.table_name()
        return Injector().get(DBClient).delete_item(table_name, key)    
    
    @classmethod
    def find(cls, key):
        table_name = cls.table_name()
        item = Injector().get(DBClient).get_item(table_name, key)
        return cls.from_item(item)

    @classmethod
    def as_item(cls, dict_data):
        item = {}
        for key, value in dict_data.items():
            if isinstance(value, str):
                item[key] = {"S": value}
            elif isinstance(value, int):
                item[key] = {"N": str(value)}
            elif isinstance(value, dict):
                item[key] = {"M": cls.as_item(value)}
            elif isinstance(value, list):
                item[key] = {"L": [cls.as_item(v) for v in value]}
        return item
    
    @classmethod
    def from_item(cls, item):
        if not item:
            return None
        data = {}
        for key, value in item.items():
            if not isinstance(value, dict):
                continue
            if "S" in value:
                data[key] = value["S"]
            elif "N" in value:
                data[key] = int(value["N"])
            elif "M" in value:
                data[key] = cls.from_item(value["M"])
            elif "L" in value:
                data[key] = [cls.from_item(v) for v in value["L"]]                
        return cls(**data)
    

