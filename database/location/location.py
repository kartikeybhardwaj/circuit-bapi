from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime
from constants.dbpath import db_path

class DBLocation:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient(db_path)
        self.__db = self.__client.circuit

    def countDocumentsByCityCountry(self, city: str, country: str) -> int:
        return self.__db.locations.count_documents({
            "city": city,
            "country": country
        })

    def countDocumentsById(self, locationId: str) -> int:
        return self.__db.locations.count_documents({
            "_id": ObjectId(locationId)
        })

    def getLocationIdByCityCountry(self, city: str, country: str) -> str:
        _id = self.__db.locations.find_one({
            "city": city,
            "country": country
        }, {
            "_id": 1
        })
        return str(_id["_id"]) if _id else None

    def getAllLocations(self) -> dict:
        result = self.__db.locations.find({
            "isActive": True
        }, {
            "_id": 1,
            "city": 1,
            "country": 1,
            "meta": 1
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
