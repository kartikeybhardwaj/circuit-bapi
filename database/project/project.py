from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

class DBProject:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def countDocumentsById(self, projectId: str) -> int:
        return self.__db.projects.count_documents({
            "_id": ObjectId(projectId)
        })

    def getAllProjects(self) -> dict:
        result = self.__db.projects.find({
            "isActive": True
        })
        return json.loads(dumps(result))

    def getProjectsByIds(self, projectIds: "list of str") -> dict:
        projectIds = list(map(ObjectId, projectIds))
        result = self.__db.projects.find({
            "_id": {
                "$in": projectIds
            },
            "isActive": True
        })
        return json.loads(dumps(result))

    def getFieldsById(self, projectId: str) -> "list of dict":
        result = self.__db.metaProjects.find({
            "_id": ObjectId(projectId),
            "isActive": True
        }, {
            "_id": 0,
            "fields": 1
        })
        return json.loads(dumps(result))[0]["fields"]

    def getRoleIdOfUserInProject(self, projectId: str, userId: str) -> str:
        result = self.__db.projects.find({
            "_id": ObjectId(projectId),
            "isActive": True,
            "members.userId": ObjectId(userId)
        }, {
            "_id": 0,
            "members.$": 1
        })
        return str(result["members"][0]["roleId"]) if result else None

    def insertMetaProject(self, metaProject: dict) -> str:
        _id = self.__db.metaProjects.insert_one(metaProject).inserted_id
        return str(_id)

    def insertProject(self, project: dict) -> str:
        _id = self.__db.projects.insert_one(project).inserted_id
        return str(_id)

    def insertMilestoneIdToProject(self, projectId: str, milestoneId: str) -> bool:
        return self.__db.projects.update_one({
            "_id": ObjectId(projectId)
        }, {
            "$push": {
                "milestonesList": ObjectId(milestoneId)
            }
        }).modified_count == 1
