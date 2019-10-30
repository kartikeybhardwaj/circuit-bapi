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

    def getIdByUsername(self, username: str) -> str:
        _id = self.__db.users.find_one({
            "username": username
        }, {
            "_id": 1
        })
        return str(_id["_id"]) if _id else None

    def checkIfUserIsSuperuser(self, _id: str) -> bool:
        return self.__db.users.count_documents({
            "_id": ObjectId(_id),
            "isSuperuser": True
        }) == 1

    def getAccessibleProjects(self, username: str) -> list:
        result = self.__db.users.find({
            "username": username
        }, {
            "_id": 0,
            "access.projectId": 1
        })
        return json.loads(dumps(result))

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
