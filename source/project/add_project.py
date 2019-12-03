import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

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

dbu = DBUser()
dbr = DBRole()
dbc = DBCounter()
dbpr = DBProject()
aur = AddUserResource()

class AddProjectResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_project_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    def validateMembersRole(self, members: "list of dict") -> [bool, str]:
        success = True
        message = ""
        # for all members, validate roleId
        for member in members:
            try:
                ObjectId(member["roleId"])
                # check if roleId exists
                if dbr.countDocumentsById(member["roleId"]) != 1:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "roleId does not exist"))
                    success = False
                    message = "Invalid member roleId"
                    break
            except Exception as ex:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
                success = False
                message = "Invalid member ObjectId"
                break
        return [success, message]

    def validateProjectMetaId(self, projectMetaId: "str or None", fields: "list of dict") -> [bool, str]:
        success = True
        message = ""
        # it's wrong if:
        ## or, projectMetaId is None and fields exists
        ## or, projectMetaId is not None and fields does not exists
        if (not projectMetaId and len(fields) > 0) or (projectMetaId and len(fields) == 0):
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "projectMetaId and fields mismatch"))
            success = False
            message = "Invalid projectMetaId"
        else:
            # validate projectMetaId
            if projectMetaId:
                try:
                    ObjectId(projectMetaId)
                except Exception as ex:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
                    success = False
                    message = "Invalid projectMetaId"
                if success:
                    # prepare fieldsDict map
                    fieldsDict = {}
                    for field in fields:
                        fieldsDict[field["key"]] = field["value"]
                    # get dbFields using projectMetaId
                    dbFields = dbpr.getFieldsById(projectMetaId)
                    # validate fields
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

    def prepareDataToBeInserted(self, index: int, requestObj: dict, userId: str) -> dict:
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["title"] = requestObj["title"]
        dataToBeInserted["isActive"] = True
        dataToBeInserted["description"] = requestObj["description"]
        dataToBeInserted["visibility"] = requestObj["visibility"]
        dataToBeInserted["projectMetaId"] = ObjectId(requestObj["projectMetaId"]) if requestObj["projectMetaId"] else None
        dataToBeInserted["fields"] = requestObj["fields"]
        dataToBeInserted["members"] = requestObj["members"]
        dataToBeInserted["milestonesList"] = []
        dataToBeInserted["meta"] = {
            "addedBy": ObjectId(userId),
            "addedOn": datetime.datetime.utcnow(),
            "lastUpdatedBy": None,
            "lastUpdatedOn": None
        }
        return dataToBeInserted

    def prepareMembersForDataToBeInserted(self, dataToBeInserted: dict, userId: str) -> dict:
        isOwnerAdded = False
        for member in dataToBeInserted["members"]:
            thisUserId = dbu.getIdByUsername(member["username"])
            # if user doesn't exist, add
            if not thisUserId:
                thisUserId = aur.addUser(member["username"], member["displayname"], userId)
            del member["username"]
            del member["displayname"]
            member["userId"] = ObjectId(thisUserId)
            member["roleId"] = ObjectId(member["roleId"])
            # check if user is adding himself
            if thisUserId == userId:
                isOwnerAdded = True
                member["roleId"] = ObjectId(dbr.getOwnerRoleId())
        # add owner role if not added
        if not isOwnerAdded:
            dataToBeInserted["members"].append({
                "userId": ObjectId(userId),
                "roleId": ObjectId(dbr.getOwnerRoleId())
            })
        return dataToBeInserted

    def insertAccessProjectIdForMember(self, dataToBeInserted: dict, projectId: str) -> None:
        for member in dataToBeInserted["members"]:
            dbu.insertAccessProjectId(str(member["userId"]), projectId)

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
        # validate schema
        afterValidation = self.validateSchema(requestObj)
        if not afterValidation[0]:
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "schema validation failed"))
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            log.info((thisFilename, inspect.currentframe().f_code.co_name, "schema validation successful"))
            try:
                # validate members role
                afterValidationMembers = self.validateMembersRole(requestObj["members"])
                if not afterValidationMembers[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationMembers[1]
                else:
                    # validate metaProject
                    afterValidationProjectMeta = self.validateProjectMetaId(requestObj["projectMetaId"], requestObj["fields"])
                    if not afterValidationProjectMeta[0]:
                        responseObj["responseId"] = 110
                        responseObj["message"] = afterValidationProjectMeta[1]
                    else:
                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "all validations passed"))
                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing data to insert"))
                        # 01. get index for new project
                        index = dbc.getNewProjectIndex()
                        # 02. increment project counter
                        dbc.incrementProjectIndex()
                        # 03. prepare DataToBeInserted
                        dataToBeInserted = self.prepareDataToBeInserted(index, requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                        # 04. prepare MembersForDataToBeInserted
                        dataToBeInserted = self.prepareMembersForDataToBeInserted(dataToBeInserted, req.params["kartoon-fapi-incoming"]["_id"])
                        # 05. insert project
                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                        projectId = dbpr.insertProject(dataToBeInserted)
                        # 06. for every member, insertAccessProjectId
                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                        self.insertAccessProjectIdForMember(dataToBeInserted, projectId)
                        # 07. attach projectId in response
                        responseObj["data"]["_id"] = projectId
                        # 08. set responseId to success
                        responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
