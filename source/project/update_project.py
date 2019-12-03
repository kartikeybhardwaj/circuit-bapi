import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_update_project import validate_update_project_schema

from database.user.user import DBUser
from database.role.role import DBRole
from database.counter.counter import DBCounter
from database.project.project import DBProject
from database.pulse.pulse import DBPulse
from source.user.add_user import AddUserResource

dbu = DBUser()
dbr = DBRole()
dbc = DBCounter()
dbpr = DBProject()
dbpu = DBPulse()
aur = AddUserResource()

class UpdateProjectResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_update_project_schema)
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

    def verifyProjectCreationAccess(self, projectId: str, userId: str) -> bool:
        roleId = dbpr.getRoleIdOfUserInProject(projectId, userId)
        return dbr.hasProjectCreationAccess(roleId)

    def prepareDataToBeUpdated(self, requestObj: dict, userId: str) -> dict:
        dataToBeUpdated = {}
        dataToBeUpdated["title"] = requestObj["title"]
        dataToBeUpdated["description"] = requestObj["description"]
        dataToBeUpdated["visibility"] = requestObj["visibility"]
        dataToBeUpdated["projectMetaId"] = ObjectId(requestObj["projectMetaId"]) if requestObj["projectMetaId"] else None
        dataToBeUpdated["fields"] = requestObj["fields"]
        dataToBeUpdated["members"] = requestObj["members"]
        dataToBeUpdated["meta"] = {
            "lastUpdatedBy": ObjectId(userId),
            "lastUpdatedOn": datetime.datetime.utcnow()
        }
        return dataToBeUpdated

    def prepareMembersForDataToBeUpdated(self, dataToBeUpdated: dict, userId: str) -> dict:
        for member in dataToBeUpdated["members"]:
            thisUserId = dbu.getIdByUsername(member["username"])
            # if user doesn't exist, add
            if not thisUserId:
                thisUserId = aur.addUser(member["username"], member["displayname"], userId)
            del member["username"]
            del member["displayname"]
            member["userId"] = ObjectId(thisUserId)
            member["roleId"] = ObjectId(member["roleId"])
        return dataToBeUpdated

    def insertAccessProjectIdForMember(self, projectId: str, members: "list of str") -> None:
        for username in members:
            userId = dbu.getIdByUsername(username)
            dbu.insertAccessProjectId(userId, projectId)

    def removeAccessFromProjectForMembers(self, projectId: str, members: "list of str") -> None:
        for username in members:
            userId = dbu.getIdByUsername(username)
            userPulses = dbu.getAccessibleUserPulsesInProjectId(userId, projectId)
            for pulseId in userPulses:
                dbpu.removeAssigneeFromPulse(userId, pulseId)
            dbu.removeAccessFromProject(userId, projectId)

    """
    REQUEST:
        projectId: str
        title: str
        description: str
        visibility: str
        members: list
        membersTodo: dict
            toAdd: list of str
            toRemove: list of str
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
                if (not self.verifyProjectCreationAccess(requestObj["projectId"], req.params["kartoon-fapi-incoming"]["_id"])
                    and not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"])):
                    # check if user has projectCreationAccess or superuser access
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "does not have projectCreationAccess nor is superuser"))
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
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
                            log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing data to update"))
                            # 01. prepare DataToBeUpdated
                            dataToBeUpdated = self.prepareDataToBeUpdated(requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                            # 02. prepare MembersForDataToBeUpdated
                            dataToBeUpdated = self.prepareMembersForDataToBeUpdated(dataToBeUpdated, req.params["kartoon-fapi-incoming"]["_id"])
                            # 03. insert project
                            log.info((thisFilename, inspect.currentframe().f_code.co_name, "updating data"))
                            dbpr.updateProject(requestObj["projectId"], dataToBeUpdated)
                            # 04. for every member to be removed, removeAccessFromProjectForMembers
                            log.info((thisFilename, inspect.currentframe().f_code.co_name, "removing data"))
                            self.removeAccessFromProjectForMembers(requestObj["projectId"], requestObj["membersTodo"]["toRemove"])
                            # 05. for every member added, insertAccessProjectIdForMember
                            log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                            self.insertAccessProjectIdForMember(requestObj["projectId"], requestObj["membersTodo"]["toAdd"])
                            # 06. set responseId to success
                            responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
