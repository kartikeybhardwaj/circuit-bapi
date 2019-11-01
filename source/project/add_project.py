from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_add_project import validate_add_project_schema

from database.user.user import DBUser
from database.role.role import DBRole
from database.counter.counter import DBCounter
from database.project.project import DBProject
from source.user.add_user import AddUserResource

class AddProjectResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_project_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def validateMembers(self, members: "list of dict") -> [bool, str]:
        success = True
        message = ""
        dbr = DBRole()
        for member in members:
            try:
                ObjectId(member["roleId"])
                if dbr.countDocumentsById(member["roleId"]) != 1:
                    success = False
                    message = "Invalid member roleId"
                    break
            except Exception as ex:
                success = False
                message = "Invalid member ObjectId"
                break
        return [success, message]

    def validateProjectMetaId(self, projectMetaId: "str or None", fields: "list of dict") -> [bool, str]:
        success = True
        message = ""
        if (not projectMetaId and len(fields) > 0) or (projectMetaId and len(fields) == 0):
            success = False
            message = "Invalid projectMetaId"
        else:
            if projectMetaId:
                try:
                    ObjectId(projectMetaId)
                except Exception as ex:
                    success = False
                    message = "Invalid projectMetaId"
            if success:
                fieldsDict = {}
                for field in fields:
                    fieldsDict[field["key"]] = field["value"]
                dbpr = DBProject()
                dbFields = dbpr.getFieldsById(projectMetaId)
                if len(fieldsDict) == len(dbFields):
                    for dbField in dbFields:
                        if dbField["key"] in fieldsDict:
                            if dbField["valueType"] == "select":
                                if not fieldsDict[dbField["key"]] in dbField["value"]:
                                    success = False
                                    message = "Invalid value for " + dbField["key"]
                                    break
                        else:
                            success = False
                            message = "Missing " + dbField["key"]
                            break
                else:
                    success = False
                    message = "Invalid fields count"
        return [success, message]

    """
    REQUEST:
        title: str
        description: str
        visibility: str
        members: list
        projectMetaId: str
        fields: list
    """
    def on_post(self, req, resp):
        requestObj = req.media
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        afterValidation = self.validateSchema(requestObj)
        if not afterValidation[0]:
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            try:
                afterValidationMembers = self.validateMembers(requestObj["members"])
                afterValidationProjectMeta = self.validateProjectMetaId(requestObj["projectMetaId"], requestObj["fields"])
                if not afterValidationMembers[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationMembers[1]
                elif not afterValidationProjectMeta[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationProjectMeta[1]
                else:
                    dbc = DBCounter()
                    index = dbc.getNewProjectIndex()
                    dbc.incrementProjectIndex()
                    dataToBeInserted = {}
                    dataToBeInserted["index"] = index
                    dataToBeInserted["title"] = requestObj["title"]
                    dataToBeInserted["isActive"] = True
                    dataToBeInserted["description"] = requestObj["description"]
                    dataToBeInserted["visibility"] = requestObj["visibility"]
                    dataToBeInserted["projectMetaId"] = ObjectId(requestObj["projectMetaId"])
                    dataToBeInserted["fields"] = requestObj["fields"]
                    dataToBeInserted["members"] = requestObj["members"]
                    dataToBeInserted["milestonesList"] = []
                    dataToBeInserted["meta"] = {
                        "addedBy": ObjectId(req.params["kartoon-fapi-incoming"]["_id"]),
                        "addedOn": datetime.datetime.utcnow(),
                        "lastUpdatedBy": None,
                        "lastUpdatedOn": None
                    }
                    dbu = DBUser()
                    for member in dataToBeInserted["members"]:
                        userId = dbu.getIdByUsername(member["username"])
                        if not userId:
                            aur = AddUserResource()
                            userId = aur.addUser(member["username"], member["displayname"], req.params["kartoon-fapi-incoming"]["_id"])
                        del member["username"]
                        del member["displayname"]
                        member["userId"] = ObjectId(userId)
                        member["roleId"] = ObjectId(member["roleId"])
                    dbpr = DBProject()
                    projectId = dbpr.insertProject(dataToBeInserted)
                    for member in dataToBeInserted["members"]:
                        dbu.insertAccessProjectId(str(member["userId"]), projectId)
                    responseObj["data"]["_id"] = projectId
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = str(ex)
        resp.media = responseObj
