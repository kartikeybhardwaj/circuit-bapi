from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

class DBPulse:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def countDocumentsById(self, projectId: str) -> int:
        return self.__db.pulses.count_documents({
            "_id": ObjectId(projectId)
        })

    def getAllPulses(self) -> dict:
        result = self.__db.pulses.find({
            "isActive": True
        })
        return json.loads(dumps(result))

    def getPulsesByIds(self, pulseIds: "list of ObjectId") -> dict:
        pulseIds = list(map(ObjectId, pulseIds))
        result = self.__db.pulses.find({
            "_id": {
                "$in": pulseIds
            },
            "isActive": True
        })
        return json.loads(dumps(result))

    def getFieldsById(self, pulseId: str) -> "list of dict":
        return self.__db.metaPulses.find_one({
            "_id": ObjectId(pulseId),
            "isActive": True
        }, {
            "_id": 0,
            "fields": 1
        })["fields"]

    def insertMetaPulse(self, metaPulse: dict) -> str:
        _id = self.__db.metaPulses.insert_one(metaPulse).inserted_id
        return str(_id)

    def insertPulse(self, pulse: dict) -> str:
        _id = self.__db.pulses.insert_one(pulse).inserted_id
        return str(_id)
