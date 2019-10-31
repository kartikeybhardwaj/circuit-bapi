from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

class DBLocation:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def countDocumentsByName(self, name: str) -> int:
        return self.__db.locations.count_documents({
            "name": name
        })

    def countDocumentsById(self, locationId: str) -> int:
        return self.__db.locations.count_documents({
            "_id": ObjectId(locationId)
        })

    def getLocationIdByName(self, name: str) -> str:
        _id = self.__db.locations.find_one({
            "name": name
        }, {
            "_id": 1
        })
        return str(_id["_id"]) if _id else None

    def getAllLocations(self) -> dict:
        result = self.__db.locations.find({
            "isActive": True
        })
        return json.loads(dumps(result))

    def getLocationsByIds(self, locationIds: "list of ObjectId") -> dict:
        result = self.__db.locations.find({
            "_id": {
                "$in": locationIds
            },
            "isActive": True
        })
        return json.loads(dumps(result))

    def insertLocations(self, locations: "list of dict") -> "list of str":
        _ids = self.__db.locations.insert_many(locations).inserted_ids
        return [str(_id) for _id in _ids]
