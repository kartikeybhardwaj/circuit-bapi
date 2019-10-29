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

    def getAllMilestones(self) -> dict:
        result = self.__db.milestones.find({
            "isActive": True
        })
        return json.loads(dumps(result))

    def getMilestonesByIds(self, _ids: "list of ObjectId") -> dict:
        result = self.__db.milestones.find({
            "_id": {
                "$in": _ids
            },
            "isActive": True
        })
        return json.loads(dumps(result))

    def insertMetaMilestone(self, metaMilestone: dict) -> str:
        _id = self.__db.metaMilestone.insert_one(metaMilestone).inserted_id
        return str(_id)

    def insertMilestone(self, milestone: dict) -> str:
        _id = self.__db.milestones.insert_one(milestone).inserted_id
        return str(_id)
