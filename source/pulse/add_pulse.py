import inspect
from utils.log import logger as log
thisFilename = __file__.split("/")[-1]

from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_add_pulse import validate_add_pulse_schema

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

class AddPulseResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_pulse_schema)
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

    def prepareDataToBeInserted(self, index: int, requestObj: dict, userId: str) -> dict:
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["isActive"] = True
        dataToBeInserted["title"] = requestObj["title"]
        dataToBeInserted["description"] = requestObj["description"]
        dataToBeInserted["color"] = requestObj["color"]
        dataToBeInserted["assignees"] = []
        for assigneeId in requestObj["assignees"]:
            dataToBeInserted["assignees"].append(ObjectId(assigneeId))
        dataToBeInserted["timeline"] = requestObj["timeline"]
        dataToBeInserted["timeline"]["begin"] = utils.getDateFromUTCString(dataToBeInserted["timeline"]["begin"])
        dataToBeInserted["timeline"]["end"] = utils.getDateFromUTCString(dataToBeInserted["timeline"]["end"])
        dataToBeInserted["comments"] = []
        dataToBeInserted["pulseMetaId"] = ObjectId(requestObj["pulseMetaId"]) if requestObj["pulseMetaId"] else None
        dataToBeInserted["fields"] = requestObj["fields"]
        dataToBeInserted["linkedProjectId"] = ObjectId(requestObj["linkedProjectId"])
        dataToBeInserted["linkedMilestoneId"] = ObjectId(requestObj["linkedMilestoneId"])
        dataToBeInserted["meta"] = {
            "addedBy": ObjectId(userId),
            "addedOn": datetime.datetime.utcnow(),
            "lastUpdatedBy": None,
            "lastUpdatedOn": None
        }
        return dataToBeInserted

    def insertAccessToPulseForAssignees(self, requestObj: dict, pulseId: str) -> None:
        for userId in requestObj["assignees"]:
            if not dbu.hasMilestoneAccess(userId, requestObj["linkedProjectId"], requestObj["linkedMilestoneId"]):
                dbu.insertAccessToMilestone(userId, requestObj["linkedProjectId"], requestObj["linkedMilestoneId"])
            dbu.insertAccessToPulse(userId, requestObj["linkedProjectId"], requestObj["linkedMilestoneId"], pulseId)

    """
    REQUEST:
        title: str
        description: str
        timeline: dict
            begin: datetime
            end: datetime
        color: str
        assignees: list of str
        pulseMetaId: str
        fields: list
        linkedProjectId: str
        linkedMilestoneId: str
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
                afterValidationLinkedProjectId = self.validateLinkedProjectId(requestObj["linkedProjectId"])
                if not afterValidationLinkedProjectId[0]:
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid linkedProjectId"))
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationLinkedProjectId[1]
                elif (not self.verifyPulseCreationAccess(requestObj["linkedProjectId"], req.params["kartoon-fapi-incoming"]["_id"])
                    and not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"])):
                    # check if user has pulseCreationAccess or superuser access
                    log.warn((thisFilename, inspect.currentframe().f_code.co_name, "does not have pulseCreationAccess nor is superuser"))
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    # validate linkedMilestoneId
                    afterValidationLinkedMilestoneId = self.validateLinkedMilestoneId(requestObj["linkedProjectId"], requestObj["linkedMilestoneId"])
                    if not afterValidationLinkedMilestoneId[0]:
                        log.warn((thisFilename, inspect.currentframe().f_code.co_name, "invalid linkedMilestoneId"))
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
                                afterValidationAssignees = self.validateAssigneesInAProject(requestObj["linkedProjectId"], requestObj["assignees"])
                                if len(afterValidationAssignees[1]) > 0:
                                    # if there exist invalid assignee
                                    responseObj["responseId"] = 110
                                    responseObj["message"] = "Invalid assignees"
                                    responseObj["data"]["validAssignees"] = afterValidationAssignees[0]
                                    responseObj["data"]["invalidAssignees"] = afterValidationAssignees[1]
                                else:
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "all validations passed"))
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "preparing data to insert"))
                                    # 01. get index for new pulse
                                    index = dbc.getNewPulseIndex()
                                    # 02. increment pulse counter
                                    dbc.incrementPulseIndex()
                                    # 03. prepare DataToBeInserted
                                    dataToBeInserted = self.prepareDataToBeInserted(index, requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                                    # 04. insertPulse
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                                    pulseId = dbpu.insertPulse(dataToBeInserted)
                                    # 05. insertPulseIdToMilestone
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                                    dbm.insertPulseIdToMilestone(requestObj["linkedMilestoneId"], pulseId)
                                    # 06. for every assignee, insertAccessToPulse
                                    log.info((thisFilename, inspect.currentframe().f_code.co_name, "inserting data"))
                                    self.insertAccessToPulseForAssignees(requestObj, pulseId)
                                    # 07. attach pulseId in response
                                    responseObj["data"]["_id"] = pulseId
                                    # 08. set responseId to success
                                    responseObj["responseId"] = 211
            except Exception as ex:
                log.error((thisFilename, inspect.currentframe().f_code.co_name), exc_info=True)
                responseObj["message"] = str(ex)
        resp.media = responseObj
