from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

class DBRole:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def getAllRoles(self) -> dict:
        result = self.__db.roles.find({
            "isActive": True
        })
        return json.loads(dumps(result))

    def getRolesByIds(self, _ids: "list of ObjectId") -> dict:
        result = self.__db.roles.find({
            "_id": {
                "$in": _ids
            },
            "isActive": True
        })
        return json.loads(dumps(result))

    def insertRole(self, role: dict) -> str:
        _id = self.__db.roles.insert_one(role).inserted_id
        return str(_id)
