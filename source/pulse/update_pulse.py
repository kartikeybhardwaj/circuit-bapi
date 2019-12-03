import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_update_pulse import validate_update_pulse_schema

from utils.utils import Utils
from database.user.user import DBUser
from database.role.role import DBRole
from database.counter.counter import DBCounter
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone
from database.pulse.pulse import DBPulse

utils = Utils()
dbu = DBUser()
dbr = DBRole()
dbc = DBCounter()
dbpr = DBProject()
dbm = DBMilestone()
dbpu = DBPulse()

class UpdatePulseResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_update_pulse_schema)
            success = True
        except Exception as ex:
            log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
            message = ex.message
        return [success, message]

    def validateTimeline(self, timeline: dict) -> [bool, str]:
        success = True
        message = ""
        tbegin = utils.getDateFromUTCString(timeline["begin"])
        tend = utils.getDateFromUTCString(timeline["end"])
        # end should be greater than begin
        if not (tend > tbegin):
            success = False
            message = "Invalid timeline"
        return [success, message]

    def validatePulseMetaId(self, pulseMetaId: "str or None", fields: "list of dict") -> [bool, str]:
        success = True
        message = ""
        # it's wrong if:
        ## or, pulseMetaId is None and fields exists
        ## or, pulseMetaId is not None and fields does not exists
        if (not pulseMetaId and len(fields) > 0) or (pulseMetaId and len(fields) == 0):
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "pulseMetaId and fields mismatch"))
            success = False
            message = "Invalid pulseMetaId"
        else:
            # validate pulseMetaId
            if pulseMetaId:
                try:
                    ObjectId(pulseMetaId)
                except Exception as ex:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
                    success = False
                    message = "Invalid pulseMetaId"
                if success:
                    # prepare fieldsDict map
                    fieldsDict = {}
                    for field in fields:
                        fieldsDict[field["key"]] = field["value"]
                    # get dbFields using projectMetaId
                    dbFields = dbpu.getFieldsById(pulseMetaId)
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

    def validateLinkedProjectId(self, linkedProjectId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(linkedProjectId)
        except Exception as ex:
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
            success = False
            message = "Invalid linkedProjectId"
        if success:
            # check if linkedProjectId exists
            if dbpr.countDocumentsById(linkedProjectId) != 1:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "linkedProjectId does not exists"))
                success = False
                message = "Invalid linkedProjectId"
        return [success, message]

    def validateLinkedMilestoneId(self, linkedProjectId: str, linkedMilestoneId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(linkedMilestoneId)
        except Exception as ex:
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
            success = False
            message = "Invalid linkedMilestoneId"
        if success:
            # check if linkedMilestoneId exists and has linkedProjectId
            if dbm.countDocumentsById(linkedMilestoneId) != 1 or not dbm.hasThisLinkedProjectId(linkedProjectId, linkedMilestoneId):
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "linkedMilestoneId does not exist or does not jave linkedProjectId"))
                success = False
                message = "Invalid linkedMilestoneId"
        return [success, message]

    def validatePulseId(self, linkedMilestoneId: str, pulseId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(pulseId)
        except Exception as ex:
            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
            success = False
            message = "Invalid pulseId"
        if success:
            # check if pulseId exists and has linkedMilestoneId
            if dbpu.countDocumentsById(pulseId) != 1 or not dbpu.hasThisLinkedMilestoneId(linkedMilestoneId, pulseId):
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "pulseId does not exist or does not jave linkedMilestoneId"))
                success = False
                message = "Invalid pulseId"
        return [success, message]

    def verifyPulseCreationAccess(self, linkedProjectId: str, userId: str) -> bool:
        roleId = dbpr.getRoleIdOfUserInProject(linkedProjectId, userId)
        return dbr.hasPulseCreationAccess(roleId)

    def validateAssigneesInAProject(self, linkedProjectId: str, assignees: "list of str") -> [list, list]:
        validAssignees = []
        invalidAssignees = []
        # for all assignees, check if they are member of linkedProjectId
        for assigneeId in assignees:
            try:
                ObjectId(assigneeId)
                if dbpr.hasThisMember(linkedProjectId, assigneeId): validAssignees.append(assigneeId)
                else: invalidAssignees.append(assigneeId)
            except Exception as ex:
                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid object id"))
                invalidAssignees.append(assigneeId)
        return [validAssignees, invalidAssignees]

    def prepareDataToBeUpdated(self, requestObj: dict, userId: str) -> dict:
        dataToBeUpdated = {}
        dataToBeUpdated["title"] = requestObj["title"]
        dataToBeUpdated["description"] = requestObj["description"]
        dataToBeUpdated["color"] = requestObj["color"]
        dataToBeUpdated["assignees"] = []
        for assigneeId in requestObj["assignees"]:
            dataToBeUpdated["assignees"].append(ObjectId(assigneeId))
        dataToBeUpdated["timeline"] = requestObj["timeline"]
        dataToBeUpdated["timeline"]["begin"] = utils.getDateFromUTCString(dataToBeUpdated["timeline"]["begin"])
        dataToBeUpdated["timeline"]["end"] = utils.getDateFromUTCString(dataToBeUpdated["timeline"]["end"])
        dataToBeUpdated["pulseMetaId"] = ObjectId(requestObj["pulseMetaId"]) if requestObj["pulseMetaId"] else None
        dataToBeUpdated["fields"] = requestObj["fields"]
        dataToBeUpdated["meta"] = {
            "lastUpdatedBy": ObjectId(userId),
            "lastUpdatedOn": datetime.datetime.utcnow()
        }
        return dataToBeUpdated

    def insertAccessToPulseForNewAssignees(self, pulseId: str, milestoneId: str, projectId: str, newAssignees: "list of str") -> None:
        for userId in newAssignees:
            if not dbu.hasMilestoneAccess(userId, projectId, milestoneId):
                dbu.insertAccessToMilestone(userId, projectId, milestoneId)
            dbu.insertAccessToPulse(userId, projectId, milestoneId, pulseId)

    def removeAccessFromPulseForAssignees(self, pulseId: str, milestoneId: str, projectId: str, assignees: "list of str") -> None:
        for userId in assignees:
            dbu.removeAccessFromPulse(userId, projectId, milestoneId, pulseId)
            if (dbu.getAccessPulseLength(userId, projectId, milestoneId) == 0):
                dbu.removeAccessFromMilestone(userId, projectId, milestoneId)

    """
    REQUEST:
        projectId: str
        milestoneId: str
        pulseId: str
        title: str
        description: str
        timeline: dict
            begin: datetime
            end: datetime
        color: str
        assignees: list of str
        assigneesTodo: dict
            toAdd: list of str
            toRemove: list of str
        pulseMetaId: str
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
                # validate linkedProjectId
                afterValidationLinkedProjectId = self.validateLinkedProjectId(requestObj["projectId"])
                if not afterValidationLinkedProjectId[0]:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid linkedProjectId"))
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationLinkedProjectId[1]
                elif (not self.verifyPulseCreationAccess(requestObj["projectId"], req.params["kartoon-fapi-incoming"]["_id"])
                    and not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"])):
                    # check if user has pulseCreationAccess or superuser access
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "does not have pulseCreationAccess nor is superuser"))
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    # validate linkedMilestoneId
                    afterValidationLinkedMilestoneId = self.validateLinkedMilestoneId(requestObj["projectId"], requestObj["milestoneId"])
                    if not afterValidationLinkedMilestoneId[0]:
                        log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid linkedMilestoneId"))
                        responseObj["responseId"] = 110
                        responseObj["message"] = afterValidationLinkedMilestoneId[1]
                    else:
                        # validate pulseId
                        afterValidationPulseId = self.validatePulseId(requestObj["milestoneId"], requestObj["pulseId"])
                        if not afterValidationLinkedMilestoneId[0]:
                            log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid pulseId"))
                            responseObj["responseId"] = 110
                            responseObj["message"] = afterValidationLinkedMilestoneId[1]
                        else:
                            # validate timeline
                            afterValidationTimeline = self.validateTimeline(requestObj["timeline"])
                            if not afterValidationTimeline[0]:
                                log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid timeline"))
                                responseObj["responseId"] = 110
                                responseObj["message"] = afterValidationTimeline[1]
                            else:
                                # validate pulseMeta
                                afterValidationPulseMeta = self.validatePulseMetaId(requestObj["pulseMetaId"], requestObj["fields"])
                                if not afterValidationPulseMeta[0]:
                                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid pulseMeta"))
                                    responseObj["responseId"] = 110
                                    responseObj["message"] = afterValidationPulseMeta[1]
                                else:
                                    # validate assignees
                                    afterValidationAssignees = self.validateAssigneesInAProject(requestObj["projectId"], requestObj["assignees"])
                                    if len(afterValidationAssignees[1]) > 0:
                                        # if there exist invalid assignee
                                        responseObj["responseId"] = 110
                                        responseObj["message"] = "Invalid assignees"
                                        responseObj["data"]["validAssignees"] = afterValidationAssignees[0]
                                        responseObj["data"]["invalidAssignees"] = afterValidationAssignees[1]
                                    else:
                                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "all validations passed"))
                                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing data to update"))
                                        # 01. prepare dataToBeUpdated
                                        dataToBeUpdated = self.prepareDataToBeUpdated(requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                                        # 02. update pulse
                                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "updating data"))
                                        dbpu.updatePulse(requestObj["pulseId"], dataToBeUpdated)
                                        # 03. for every new assignee, insertAccessToPulse
                                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                                        self.insertAccessToPulseForNewAssignees(requestObj["pulseId"], requestObj["milestoneId"], requestObj["projectId"], requestObj["assigneesTodo"]["toAdd"])
                                        # 04. for every assignee to be removed, removeAccessFromPulseForAssignees
                                        log.info((thisFilename, inspect.currentframe().f_code.co_name, "removing data"))
                                        self.removeAccessFromPulseForAssignees(requestObj["pulseId"], requestObj["milestoneId"], requestObj["projectId"], requestObj["assigneesTodo"]["toRemove"])
                                        # 05. set responseId to success
                                        responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
