from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

from database.counter.counter import DBCounter

class DBUser:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def countDocuments(self, username: str) -> int:
        return self.__db.users.count_documents({
            "username": username
        })

    def getUserByUsername(self, username: str) -> dict:
        result = self.__db.users.find_one({
            "username": username
        })
        return json.loads(dumps(result))

    def getIdByUsername(self, username: str) -> str:
        _id = self.__db.users.find_one({
            "username": username
        }, {
            "_id": 1
        })
        return str(_id["_id"]) if _id else None

    def checkIfUserIsSuperuser(self, userId: str) -> bool:
        return self.__db.users.count_documents({
            "_id": ObjectId(userId),
            "isSuperuser": True
        }) == 1

    def getAccessibleProjects(self, userId: str) -> list:
        result = self.__db.users.find_one({
            "_id": ObjectId(userId)
        }, {
            "_id": 0,
            "access.projects.projectId": 1
        })
        return json.loads(dumps(result))["access"]["projects"]

    def updateUserToSuperuser(self, username: str) -> bool:
        return self.__db.users.update_one({
            "username": username
        }, {
            "$set": {
                "isSuperuser": True
            }
        }).modified_count == 1

    def updateSuperuserToUser(self, username: str) -> bool:
        return self.__db.users.update_one({
            "username": username
        }, {
            "$set": {
                "isSuperuser": False
            }
        }).modified_count == 1

    def updateLastSeen(self, userId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$set": {
                "meta.lastSeen": datetime.datetime.utcnow()
            }
        }).modified_count == 1

    def insertUser(self, user: dict) -> str:
        _id = self.__db.users.insert_one(user).inserted_id
        return str(_id)

    def insertAccessProjectId(self, userId: str, projectId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$push": {
                "access.projects": {
                    "projectId": ObjectId(projectId),
                    "milestones": []
                }
            }
        }).modified_count == 1

    def canAccessMilestone(self, userId: str, projectId: str, milestoneId: str) -> bool:
        # TODO: please verify this query
        return self.__db.users.count_documents({
            "_id": ObjectId(userId),
            "access.projects.projectId": ObjectId(projectId),
            "access.projects.milestones.milestoneId": ObjectId(milestoneId)
        }) == 1

    def insertAccessToMilestone(self, userId: str, projectId: str, milestoneId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId),
            "access.projects.projectId": ObjectId(projectId)
        }, {
            "$push": {
                "access.projects.$.milestones": {
                    "milestoneId": ObjectId(milestoneId),
                    "pulses": []
                }
            }
        }).modified_count == 1

    def insertAccessToPulse(self, userId: str, projectId: str, milestoneId: str, pulseId: str) -> bool:
        return self.__db.users.update_one({
            "_id": ObjectId(userId)
        }, {
            "$push": {
                "access.projects.$[i].milestones.$[j].pulses": ObjectId(pulseId)
            }
        }, array_filters = [{
                "i.projectId": ObjectId(projectId)
        }, {
                "j.milestoneId": ObjectId(milestoneId)
        }]).modified_count == 1
