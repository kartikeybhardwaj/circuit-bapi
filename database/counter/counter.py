from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

class DBCounter:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def getNewUserIndex(self) -> int:
        return self.__db.counter.find_one({
                "for": "users"
            })["count"] + 1

    def incrementUserIndex(self) -> bool:
        return self.__db.counter.update_one({
                "for": "users"
            }, {
                "$inc": {
                    "count": 1
                }
            }).modified_count == 1
