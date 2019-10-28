from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
from typing import List
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

    def checkIfUserIsSuperuser(self, username: str) -> bool:
        return self.__db.users.count_documents({
            "username": username,
            "isSuperuser": True
        }) == 1

    def getAccessibleProjects(self, username: str) -> List[ObjectId]:
        result = self.__db.users.find({
            "username": username
        }, {
            "_id": -1,
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

    def insertSuperuser(self, index, username, displayname) -> dict:
        _id = self.__db.users.insert_one({
                "index": index,
                "username": username,
                "displayname": displayname,
                "isSuperuser": True,
                "baseLocation": None,
                "otherLocations": [],
                "nonAvailability": [],
                "access": {
                    "projects": []
                },
                "meta": {
                    "addedBy": None,
                    "addedOn": datetime.datetime.utcnow(),
                    "lastSeen": None
                }
            }).inserted_id
        return str(_id)
