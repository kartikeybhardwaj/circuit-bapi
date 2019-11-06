from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

class DBMilestone:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def countDocumentsById(self, milestoneId: str) -> int:
        return self.__db.milestones.count_documents({
            "_id": ObjectId(milestoneId),
            "isActive": True
        })

    def getAllMilestones(self) -> dict:
        result = self.__db.milestones.find({
            "isActive": True
        })
        return json.loads(dumps(result))

    def getMilestonesByIds(self, milestoneIds: "list of str") -> dict:
        milestoneIds = list(map(ObjectId, milestoneIds))
        result = self.__db.milestones.find({
            "_id": {
                "$in": milestoneIds
            },
            "isActive": True
        }, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "description": 1,
            "timeline": 1,
            "pulsesList": 1,
            "milestoneMetaId": 1,
            "fields": 1,
            "linkedProjectId": 1,
            "meta": 1
        })
        return json.loads(dumps(result))

    def getPulsesList(self, projectId: str, milestoneId: str) -> list:
        return self.__db.milestones.find_one({
            "_id": ObjectId(milestoneId),
            "linkedProjectId": ObjectId(projectId),
            "isActive": True
        }, {
            "_id": 0,
            "pulsesList": 1
        })["pulsesList"]

    def getFieldsById(self, milestoneId: str) -> "list of dict":
        return self.__db.metaMilestones.find_one({
            "_id": ObjectId(milestoneId),
            "isActive": True
        }, {
            "_id": 0,
            "fields": 1
        })["fields"]

    def getActiveMilesonteIdsByIds(self, milestoneIds: "list of str") -> "list of dict":
        milestoneIds = list(map(ObjectId, milestoneIds))
        result = self.__db.milestones.find({
            "_id": {
                "$in": milestoneIds
            },
            "isActive": True
        }, {
            "_id": 1
        })
        return json.loads(dumps(result))

    def getTitlesMapByIds(self, milestoneIds: "list of str") -> "list of dict":
        milestoneIds = list(map(ObjectId, milestoneIds))
        result = self.__db.milestones.find({
            "_id": {
                "$in": milestoneIds
            }
        }, {
            "_id": 1,
            "title": 1
        })
        return json.loads(dumps(result))

    def hasThisLinkedProjectId(self, projectId: str, milestoneId: str) -> bool:
        return self.__db.milestones.count_documents({
            "_id": ObjectId(milestoneId),
            "linkedProjectId": ObjectId(projectId)
        }) == 1

    def insertMetaMilestone(self, metaMilestone: dict) -> str:
        _id = self.__db.metaMilestones.insert_one(metaMilestone).inserted_id
        return str(_id)

    def insertMilestone(self, milestone: dict) -> str:
        _id = self.__db.milestones.insert_one(milestone).inserted_id
        return str(_id)

    def insertPulseIdToMilestone(self, milestoneId: str, pulseId: str) -> bool:
        return self.__db.milestones.update_one({
            "_id": ObjectId(milestoneId)
        }, {
            "$push": {
                "pulsesList": ObjectId(pulseId)
            }
        }).modified_count == 1
