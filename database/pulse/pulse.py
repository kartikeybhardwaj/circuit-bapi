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

    def hasThisLinkedMilestoneId(self, milestoneId: str, pulseId: str) -> bool:
        return self.__db.pulses.count_documents({
            "_id": ObjectId(pulseId),
            "linkedMilestoneId": ObjectId(milestoneId)
        }) == 1

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
        }, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "description": 1,
            "color": 1,
            "timeline": 1,
            "assignees": 1,
            "comments": 1,
            "pulseMetaId": 1,
            "fields": 1,
            "linkedProjectId": 1,
            "linkedMilestoneId": 1,
            "meta": 1
        })
        return json.loads(dumps(result))

    def getAllMetaPulses(self) -> dict:
        result = self.__db.metaPulses.find({}, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "description": 1,
            "fields": 1,
            "meta": 1
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

    def getActivePulseIdsByIds(self, pulseIds: "list of str") -> "list of dict":
        pulseIds = list(map(ObjectId, pulseIds))
        result = self.__db.pulses.find({
            "_id": {
                "$in": pulseIds
            },
            "isActive": True
        }, {
            "_id": 1
        })
        return json.loads(dumps(result))

    def getTitlesMapByIds(self, pulseIds: "list of str") -> "list of dict":
        pulseIds = list(map(ObjectId, pulseIds))
        result = self.__db.pulses.find({
            "_id": {
                "$in": pulseIds
            }
        }, {
            "_id": 1,
            "title": 1
        })
        return json.loads(dumps(result))

    def insertMetaPulse(self, metaPulse: dict) -> str:
        _id = self.__db.metaPulses.insert_one(metaPulse).inserted_id
        return str(_id)

    def insertPulse(self, pulse: dict) -> str:
        _id = self.__db.pulses.insert_one(pulse).inserted_id
        return str(_id)

    def updatePulseTimeline(self, pulseId: str, timeline: dict) -> bool:
        return self.__db.pulses.update_one({
            "_id": ObjectId(pulseId)
        }, {
            "$set": {
                "timeline": timeline
            }
        }).modified_count == 1
