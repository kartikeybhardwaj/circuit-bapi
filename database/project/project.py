from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
from typing import List
import json
import datetime

class DBProject:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def getAllProjects(self) -> dict:
        result = self.__db.projects.find({
            "isActive": True
        })
        return json.loads(dumps(result))

    def getProjectsByIds(self, _ids: List[ObjectId]) -> dict:
        result = self.__db.projects.find({
            "_id": {
                "$in": _ids
            },
            "isActive": True
        })
        return json.loads(dumps(result))

    def insertProject(self, project: dict) -> str:
        _id = self.__db.projects.insert_one(project).inserted_id
        return str(_id)
