from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import datetime

class DBRole:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client = MongoClient('mongodb://kart:oon@127.0.0.1:27017/circuit')
        self.__db = self.__client.circuit

    def getOwnerRoleId(self) -> str:
        result = self.__db.roles.find_one({
            "title": "Owner"
        }, {
            "_id": 1
        })
        return json.loads(dumps(result))["_id"]["$oid"]

    def getAllRoles(self) -> dict:
        result = self.__db.roles.find({
            "isActive": True
        }, {
            "_id": 1,
            "index": 1,
            "title": 1,
            "description": 1,
            "canModifyUsersRole": 1,
            "canModifyLocations": 1,
            "canModifyProjects": 1,
            "canModifyMilestones": 1,
            "canModifyPulses": 1,
            "meta": 1
        })
        return json.loads(dumps(result))

    def countDocumentsByTitle(self, roleTitle: str) -> int:
        return self.__db.roles.count_documents({
            "title": roleTitle,
            "isActive": True
        })

    def countDocumentsById(self, roleId: str) -> int:
        return self.__db.roles.count_documents({
            "_id": ObjectId(roleId),
            "isActive": True
        })

    def getRolesByIds(self, roleIds: "list of str") -> dict:
        roleIds = list(map(ObjectId, roleIds))
        result = self.__db.roles.find({
            "_id": {
                "$in": roleIds
            },
            "isActive": True
        })
        return json.loads(dumps(result))

    def hasMilestoneCreationAccess(self, roleId: str) -> bool:
        result = self.__db.roles.find_one({
            "_id": ObjectId(roleId),
            "isActive": True,
            "canModifyMilestones": True
        }, {
            "_id": 1
        })
        return True if result else False

    def hasPulseCreationAccess(self, roleId: str) -> bool:
        result = self.__db.roles.find_one({
            "_id": ObjectId(roleId),
            "isActive": True,
            "canModifyPulses": True
        }, {
            "_id": 1
        })
        return True if result else False

    def insertRole(self, role: dict) -> str:
        _id = self.__db.roles.insert_one(role).inserted_id
        return str(_id)
