from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_add_milestone import validate_add_milestone_schema

from utils.utils import Utils
from database.user.user import DBUser
from database.role.role import DBRole
from database.counter.counter import DBCounter
from database.project.project import DBProject
from database.milestone.milestone import DBMilestone

utils = Utils()
dbu = DBUser()
dbr = DBRole()
dbc = DBCounter()
dbpr = DBProject()
dbm = DBMilestone()

class AddMilestoneResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_milestone_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def validateTimeline(self, timeline: dict) -> [bool, str]:
        success = True
        message = ""
        utils = Utils()
        tbegin = utils.getDateFromUTCString(timeline["begin"])
        tend = utils.getDateFromUTCString(timeline["end"])
        # end should be greater than begin and end should be greater than now
        if not (tend > tbegin and tend > datetime.datetime.utcnow()):
            success = False
            message = "Invalid timeline"
        return [success, message]

    def validateMilestoneMetaId(self, milestoneMetaId: "str or None", fields: "list of dict") -> [bool, str]:
        success = True
        message = ""
        # it's wrong if:
        ## or, milestoneMetaId is None and fields exists
        ## or, milestoneMetaId is not None and fields does not exists
        if (not milestoneMetaId and len(fields) > 0) or (milestoneMetaId and len(fields) == 0):
            success = False
            message = "Invalid milestoneMetaId"
        else:
            # validate milestoneMetaId
            if milestoneMetaId:
                try:
                    ObjectId(milestoneMetaId)
                except Exception as ex:
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

    def validateLinkedProjectId(self, linkedProjectId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(linkedProjectId)
        except Exception as ex:
            success = False
            message = "Invalid linkedProjectId"
        if success:
            # check if linkedProjectId exists
            if dbpr.countDocumentsById(linkedProjectId) != 1:
                success = False
                message = "Invalid linkedProjectId"
        return [success, message]

    def verifyMilestoneCreationAccess(self, linkedProjectId: str, userId: str) -> bool:
        roleId = dbpr.getRoleIdOfUserInProject(linkedProjectId, userId)
        return dbr.hasMilestoneCreationAccess(roleId)

    def prepareDataToBeInserted(self, index: int, requestObj: dict, userId: str) -> dict:
        dataToBeInserted = {}
        dataToBeInserted["index"] = index
        dataToBeInserted["isActive"] = True
        dataToBeInserted["title"] = requestObj["title"]
        dataToBeInserted["description"] = requestObj["description"]
        dataToBeInserted["timeline"] = requestObj["timeline"]
        dataToBeInserted["milestoneMetaId"] = ObjectId(requestObj["milestoneMetaId"])
        dataToBeInserted["fields"] = requestObj["fields"]
        dataToBeInserted["pulsesList"] = []
        dataToBeInserted["linkedProjectId"] = ObjectId(requestObj["linkedProjectId"])
        dataToBeInserted["meta"] = {
            "addedBy": ObjectId(userId),
            "addedOn": datetime.datetime.utcnow(),
            "lastUpdatedBy": None,
            "lastUpdatedOn": None
        }
        return dataToBeInserted

    """
    REQUEST:
        title: str
        description: str
        timeline: dict
            begin: datetime
            end: datetime
        milestoneMetaId: str
        fields: list
        linkedProjectId: str
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
            responseObj["responseId"] = 110
            responseObj["message"] = afterValidation[1]
        else:
            try:
                # validate linkedProjectId
                afterValidationLinkedProjectId = self.validateLinkedProjectId(requestObj["linkedProjectId"])
                if not afterValidationLinkedProjectId[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationLinkedProjectId[1]
                elif (not self.verifyMilestoneCreationAccess(requestObj["linkedProjectId"], req.params["kartoon-fapi-incoming"]["_id"])
                    and not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"])):
                    # check for milestoneCreationAccess or superuser access
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    # validate timeline
                    afterValidationTimeline = self.validateTimeline(requestObj["timeline"])
                    if not afterValidationTimeline[0]:
                        responseObj["responseId"] = 110
                        responseObj["message"] = afterValidationTimeline[1]
                    else:
                        # validate milestoneMeta
                        afterValidationMilestoneMeta = self.validateMilestoneMetaId(requestObj["milestoneMetaId"], requestObj["fields"])
                        if not afterValidationMilestoneMeta[0]:
                            responseObj["responseId"] = 110
                            responseObj["message"] = afterValidationMilestoneMeta[1]
                        else:
                            # 01. get index for new milestone
                            index = dbc.getNewMilestoneIndex()
                            # 02. increment milestone counter
                            dbc.incrementMilestoneIndex()
                            # 03. prepare DataToBeInserted
                            dataToBeInserted = self.prepareDataToBeInserted(index, requestObj, req.params["kartoon-fapi-incoming"]["_id"])
                            # 04. insertMilestone
                            milestoneId = dbm.insertMilestone(dataToBeInserted)
                            # 05. insertMilestoneIdToProject
                            dbpr.insertMilestoneIdToProject(requestObj["linkedProjectId"], milestoneId)
                            # 06. attach milestoneId in response
                            responseObj["data"]["_id"] = milestoneId
                            # 07. set responseId to success
                            responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = str(ex)
        resp.media = responseObj
