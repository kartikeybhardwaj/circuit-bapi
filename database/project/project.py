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

    def getAllProjectIds(self) -> dict:
        result = self.__db.projects.find({
            "isActive": True
        }, {
            "_id": 1
        })
        return json.loads(dumps(result))

    def getPublicProjectIds(self) -> dict:
        result = self.__db.projects.find({
            "visibility": "public"
        }, {
            "_id": 1
        })
        return json.loads(dumps(result))

    def getProjectsByIds(self, projectIds: "list of str") -> dict:
        projectIds = list(map(ObjectId, projectIds))
        result = self.__db.projects.find({
            "_id": {
                "$in": projectIds
            },
            "isActive": True
        }, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "description": 1,
            "milestonesList": 1,
            "visibility": 1,
            "members": 1,
            "projectMetaId": 1,
            "fields": 1,
            "meta": 1
        })
        return json.loads(dumps(result))

    def getActiveProjectIdsByIds(self, projectIds: "list of str") -> "list of dict":
        projectIds = list(map(ObjectId, projectIds))
        result = self.__db.projects.find({
            "_id": {
                "$in": projectIds
            },
            "isActive": True
        }, {
            "_id": 1
        })
        return json.loads(dumps(result))

    def getFieldsById(self, projectId: str) -> "list of dict":
        return self.__db.metaProjects.find_one({
            "_id": ObjectId(projectId),
            "isActive": True
        }, {
            "_id": 0,
            "fields": 1
        })["fields"]

    def getRoleIdOfUserInProject(self, projectId: str, userId: str) -> str:
        result = self.__db.projects.find_one({
            "_id": ObjectId(projectId),
            "isActive": True,
            "members.userId": ObjectId(userId)
        }, {
            "_id": 0,
            "members.$": 1
        })
        return str(result["members"][0]["roleId"]) if result else None

    def hasThisAssignee(self, projectId: str, assigneeId: str) -> bool:
        return self.__db.projects.count_documents({
            "_id": ObjectId(projectId),
            "members.userId": ObjectId(assigneeId)
        }) == 1

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
