import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_update_milestone import validate_update_milestone_schema

from utils.utils import Utils
from database.user.user import DBUser
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone
from database.pulse.pulse import DBPulse
from database.role.role import DBRole
from database.location.location import DBLocation

utils = Utils()
dbu = DBUser()
dbpr = DBProject()
dbm = DBMilestone()
dbr = DBRole()
dbl = DBLocation()

# check if projectId is valid ObjectId
# does this projectId exists
# is this projectId active
# check if milestoneId is valid ObjectId
# does this milestoneId exists
# is this milestoneId active
# verify access for user
# or, is userId superuser (update this milestone)
# or, and, user member, canModifyMilestones (update this milestone)
# validate timeline
# validate locationId
# validate milestoneMetaId

class UpdateMilestoneResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_update_milestone_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def validateProjectId(self, projectId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(projectId)
        except Exception as ex:
            success = False
            message = "Invalid projectId"
        if success:
            if dbpr.countDocumentsById(projectId) != 1:
                success = False
                message = "Invalid projectId"
        return [success, message]

    def validateMilestoneId(self, milestoneId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(milestoneId)
        except Exception as ex:
            success = False
            message = "Invalid milestoneId"
        if success:
            if dbm.countDocumentsById(milestoneId) != 1:
                success = False
                message = "Invalid milestoneId"
        return [success, message]

    def verifyAccess(self, milestoneId: str, projectId: str, userId: str) -> bool:
        success = False
        if (dbu.checkIfUserIsSuperuser(userId) or
            (dbpr.hasThisMember(projectId, userId) and
            dbr.hasMilestoneCreationAccess(dbpr.getRoleIdOfUserInProject(projectId, userId)))):
            success = True
        return success

    def validateTimeline(self, timeline: dict) -> [bool, str]:
        success = True
        message = ""
        tbegin = utils.getDateFromUTCString(timeline["begin"])
        tend = utils.getDateFromUTCString(timeline["end"])
        # end should be greater than begin and end should be greater than now
        if not tend > tbegin:
            success = False
            message = "Invalid timeline"
        return [success, message]

    def validateLocationId(self, locationId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(locationId)
        except Exception as ex:
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
            success = False
            message = "Invalid locationId"
        if success:
            # check if locationId exists
            if dbl.countDocumentsById(locationId) != 1:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "locationId does not exists"))
                success = False
                message = "Invalid locationId"
        return [success, message]

    def validateMilestoneMetaId(self, milestoneMetaId: "str or None", fields: "list of dict") -> [bool, str]:
        success = True
        message = ""
        # it's wrong if:
        ## or, milestoneMetaId is None and fields exists
        ## or, milestoneMetaId is not None and fields does not exists
        if (not milestoneMetaId and len(fields) > 0) or (milestoneMetaId and len(fields) == 0):
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "milestoneMetaId and fields mismatch"))
            success = False
            message = "Invalid milestoneMetaId"
        else:
            # validate milestoneMetaId
            if milestoneMetaId:
                try:
                    ObjectId(milestoneMetaId)
                except Exception as ex:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
                    success = False
                    message = "Invalid milestoneMetaId"
                if success:
                    # prepare fieldsDict map
                    fieldsDict = {}
                    for field in fields:
                        fieldsDict[field["key"]] = field["value"]
                    # get dbFields using projectMetaId
                    dbFields = dbm.getFieldsById(milestoneMetaId)
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

    def prepareDataToBeUpdated(self, requestObj: dict, userId: str) -> dict:
        dataToBeUpdated = {}
        dataToBeUpdated["title"] = requestObj["title"]
        dataToBeUpdated["description"] = requestObj["description"]
        dataToBeUpdated["locationId"] = ObjectId(requestObj["locationId"])
        dataToBeUpdated["timeline"] = requestObj["timeline"]
        dataToBeUpdated["timeline"]["begin"] = utils.getDateFromUTCString(dataToBeUpdated["timeline"]["begin"])
        dataToBeUpdated["timeline"]["end"] = utils.getDateFromUTCString(dataToBeUpdated["timeline"]["end"])
        dataToBeUpdated["milestoneMetaId"] = ObjectId(requestObj["milestoneMetaId"]) if requestObj["milestoneMetaId"] else None
        dataToBeUpdated["fields"] = requestObj["fields"]
        dataToBeUpdated["meta"] = {
            "lastUpdatedBy": ObjectId(userId),
            "lastUpdatedOn": datetime.datetime.utcnow()
        }
        return dataToBeUpdated

    """
    REQUEST:
        projectId: str
        milestoneId: str
        title: str
        description: str
        locationId: str
        timeline: dict
            begin: str
            end: str
        milestoneMetaId: str
        fields: list of dict
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
                # validate projectId
                afterValidationProjectId = self.validateProjectId(requestObj["projectId"])
                if not afterValidationProjectId[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationProjectId[1]
                else:
                    # validate milestoneId
                    afterValidationMilestoneId = self.validateMilestoneId(requestObj["milestoneId"])
                    if not afterValidationMilestoneId[0]:
                        responseObj["responseId"] = 110
                        responseObj["message"] = afterValidationMilestoneId[1]
                    elif not dbm.hasThisLinkedProjectId(requestObj["projectId"], requestObj["milestoneId"]):
                        # validate if milestoneId is in projectId
                        responseObj["responseId"] = 110
                        responseObj["message"] = "Invalid linkedProjectId"
                    elif not self.verifyAccess(requestObj["milestoneId"], requestObj["projectId"], req.params["kartoon-fapi-incoming"]["_id"]):
                        # verify access for user
                        log.warn((thisFilename, inspect.currentframe().f_code.co_name, "user does not have milestoneCreationAccess nor is superuser"))
                        responseObj["responseId"] = 109
                        responseObj["message"] = "Unauthorized access"
                    else:
                        # validate timeline
                        afterValidationTimeline = self.validateTimeline(requestObj["timeline"])
                        if not afterValidationTimeline[0]:
                            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid timeline"))
                            responseObj["responseId"] = 110
                            responseObj["message"] = afterValidationTimeline[1]
                        else:
                            # validate loationId
                            afterValidationLocationId = self.validateLocationId(requestObj["locationId"])
                            if not afterValidationLocationId[0]:
                                responseObj["responseId"] = 110
                                responseObj["message"] = afterValidationLocationId[1]
                            else:
                                # validate milestoneMeta
                                afterValidationMilestoneMeta = self.validateMilestoneMetaId(requestObj["milestoneMetaId"], requestObj["fields"])
                                if not afterValidationMilestoneMeta[0]:
                                    responseObj["responseId"] = 110
                                    responseObj["message"] = afterValidationMilestoneMeta[1]
                                else:
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "all validations passed"))
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing data to insert"))
                                    # 01. prepare dataToBeUpdated
                                    dataToBeUpdated = self.prepareDataToBeUpdated(requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                                    # 02. update data
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "updating data"))
                                    dbm.updateMilestone(requestObj["milestoneId"], dataToBeUpdated)
                                    # 03. set responseId to success
                                    responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
