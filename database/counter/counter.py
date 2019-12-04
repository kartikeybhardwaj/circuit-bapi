from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime
from constants.dbpath import db_path

class DBCounter:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient(db_path)
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

    def getNewLocationIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "locations"
        })["count"] + 1

    def incrementLocationIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "locations"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1

    def getNewRoleIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "roles"
        })["count"] + 1

    def incrementRoleIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "roles"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1

    def getNewMetaProjectIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "metaProjects"
        })["count"] + 1

    def incrementMetaProjectIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "metaProjects"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1

    def getNewMetaMilestoneIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "metaMilestones"
        })["count"] + 1

    def incrementMetaMilestoneIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "metaMilestones"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1

    def getNewMetaPulseIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "metaPulses"
        })["count"] + 1

    def incrementMetaPulseIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "metaPulses"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1

    def getNewProjectIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "projects"
        })["count"] + 1

    def incrementProjectIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "projects"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1

    def getNewMilestoneIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "milestones"
        })["count"] + 1

    def incrementMilestoneIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "milestones"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1

    def getNewPulseIndex(self) -> int:
        return self.__db.counter.find_one({
            "for": "pulses"
        })["count"] + 1

    def incrementPulseIndex(self) -> bool:
        return self.__db.counter.update_one({
            "for": "pulses"
        }, {
            "$inc": {
                "count": 1
            }
        }).modified_count == 1
