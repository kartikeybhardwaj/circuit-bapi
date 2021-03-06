from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime
from constants.dbpath import db_path

class DBMilestone:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient(db_path)
        self.__db = self.__client.circuit

    def countDocumentsById(self, milestoneId: str) -> int:
        return self.__db.milestones.count_documents({
            "_id": ObjectId(milestoneId),
            "isActive": True
        })

    def getAllMilestones(self) -> dict:
        result = self.__db.milestones.find({
            "isActive": True
        }, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "locationId": 1,
            "timeline": 1,
            "linkedProjectId": 1
        })
        return json.loads(dumps(result))

    def getMilestoneById(self, milestoneId: str) -> dict:
        result = self.__db.milestones.find_one({
            "_id": ObjectId(milestoneId),
            "isActive": True
        }, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "description": 1,
            "timeline": 1,
            "locationId": 1,
            "pulsesList": 1,
            "milestoneMetaId": 1,
            "fields": 1,
            "linkedProjectId": 1,
            "meta": 1
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
            "locationId": 1,
            "pulsesList": 1,
            "milestoneMetaId": 1,
            "fields": 1,
            "linkedProjectId": 1,
            "meta": 1
        })
        return json.loads(dumps(result))

    def getAllMetaMilestones(self) -> dict:
        result = self.__db.metaMilestones.find({}, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "description": 1,
            "fields": 1,
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

    def getActiveMilestoneIdsByIds(self, milestoneIds: "list of str") -> "list of dict":
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

    def getLocationId(self, milestoneId: str) -> str:
        result = self.__db.milestones.find_one({
            "_id": ObjectId(milestoneId)
        }, {
            "_id": 0,
            "locationId": 1
        })
        return json.loads(dumps(result))["locationId"]["$oid"]

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

    def updateMilestone(self, milestoneId: str, dataToBeUpdated: dict) -> bool:
        return self.__db.milestones.update_one({
            "_id": ObjectId(milestoneId)
        }, {
            "$set": {
                "title": dataToBeUpdated["title"],
                "description": dataToBeUpdated["description"],
                "locationId": dataToBeUpdated["locationId"],
                "timeline": dataToBeUpdated["timeline"],
                "milestoneMetaId": dataToBeUpdated["milestoneMetaId"],
                "fields": dataToBeUpdated["fields"],
                "meta.lastUpdatedBy": dataToBeUpdated["meta"]["lastUpdatedBy"],
                "meta.lastUpdatedOn": dataToBeUpdated["meta"]["lastUpdatedOn"]
            }
        }).modified_count == 1
