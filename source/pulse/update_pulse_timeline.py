from bson.objectid import ObjectId
import datetime
import re

from jsonschema import validate

from utils.req_validator.validate_update_pulse_timeline import validate_update_pulse_timeline_schema

from database.user.user import DBUser
from database.pulse.pulse import DBPulse
from database.milestone.milestone import DBMilestone
from database.project.project import DBProject
from database.role.role import DBRole
from utils.utils import Utils

dbu = DBUser()
dbpu = DBPulse()
dbm = DBMilestone()
dbpr = DBProject()
dbr = DBRole()
utils = Utils()

# check if pulseId is valid ObjectId
# does this pulseId exists
# is this pulseId active
# does this pulseId has this linkedMilestoneId
# check if milestoneId is valid ObjectId
# does this milestoneId exists
# is this milestoneId active
# does this milestoneId has this linkedProjectId
# check if projectId is valid ObjectId
# does this projectId exists
# is this projectId active
# validate timeline
# verify user role if canModifyPulses is true

class UpdatePulseTimelineResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_update_pulse_timeline_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    def validatePulseId(self, pulseId: str, milestoneId: str) -> [bool, str]:
        success = True
        message = ""
        try:
            ObjectId(pulseId)
        except Exception as ex:
            success = False
            message = "Invalid pulseId"
        if success:
            if dbpu.countDocumentsById(pulseId) != 1:
                success = False
                message = "Invalid pulseId"
            elif not dbpu.hasThisLinkedMilestoneId(milestoneId, pulseId):
                success = False
                message = "Invalid pulseId"
        return [success, message]

    def validateMilestoneId(self, milestoneId: str, projectId: str) -> [bool, str]:
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
            elif not dbm.hasThisLinkedProjectId(projectId, milestoneId):
                success = False
                message = "Invalid milestoneId"
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

    def validateTimeline(self, timeline: dict) -> [bool, str]:
        # TODO: this timeline should exists within the timeline of milestone
        success = True
        message = ""
        tbegin = utils.getDateFromUTCString(timeline["begin"])
        tend = utils.getDateFromUTCString(timeline["end"])
        if not (tend > tbegin and tend > datetime.datetime.utcnow()):
            success = False
            message = "Invalid timeline"
        return [success, message]

    def verifyAccess(self, userId: str, projectId: str) -> bool:
        roleId = dbpr.getRoleIdOfUserInProject(projectId, userId)
        return dbr.hasPulseCreationAccess(roleId)

    """
    REQUEST:
        "pulseId": str
        "milestoneId": str
        "projectId": str
        "timeline": dict
            "begin": str
            "end": str
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
                # validate pulseId
                afterValidationPulseId = self.validatePulseId(requestObj["pulseId"], requestObj["milestoneId"])
                if not afterValidationPulseId[0]:
                    responseObj["responseId"] = 110
                    responseObj["message"] = afterValidationPulseId[1]
                else:
                    # validate milistoneId
                    afterValidationMilestoneId = self.validateMilestoneId(requestObj["milestoneId"], requestObj["projectId"])
                    if not afterValidationMilestoneId[0]:
                        responseObj["responseId"] = 110
                        responseObj["message"] = afterValidationMilestoneId[1]
                    else:
                        # validate projectId
                        afterValidationProjectId = self.validateProjectId(requestObj["projectId"])
                        if not afterValidationProjectId[0]:
                            responseObj["responseId"] = 110
                            responseObj["message"] = afterValidationProjectId[1]
                        else:
                            # validate timeline
                            afterValidationTimeline = self.validateTimeline(requestObj["timeline"])
                            if not afterValidationTimeline[0]:
                                responseObj["responseId"] = 110
                                responseObj["message"] = afterValidationTimeline[1]
                            else:
                                # verify if user has access to update this pulse
                                if not self.verifyAccess(req.params["kartoon-fapi-incoming"]["_id"], requestObj["projectId"]):
                                    responseObj["responseId"] = 109
                                    responseObj["message"] = "Unauthorized access"
                                else:
                                    # update pulse timeline
                                    dbpu.updatePulseTimeline(requestObj["pulseId"], requestObj["timeline"])
                                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = str(ex)
        resp.media = responseObj
