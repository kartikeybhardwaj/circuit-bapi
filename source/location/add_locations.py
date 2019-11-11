from bson.objectid import ObjectId
import datetime

from jsonschema import validate

from utils.req_validator.validate_add_locations import validate_add_locations_schema

from database.user.user import DBUser
from database.counter.counter import DBCounter
from database.location.location import DBLocation

dbu = DBUser()
dbc = DBCounter()
dbl = DBLocation()

class AddLocationsResource:

    def validateSchema(self, requestObj: dict) -> [bool, str]:
        success = False
        message = ""
        try:
            validate(instance=requestObj, schema=validate_add_locations_schema)
            success = True
        except Exception as ex:
            message = ex.message
        return [success, message]

    """
    REQUEST:
        "names": list of str
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
                # check if user is superuser
                if not dbu.checkIfUserIsSuperuser(req.params["kartoon-fapi-incoming"]["_id"]):
                    # if not
                    responseObj["responseId"] = 109
                    responseObj["message"] = "Unauthorized access"
                else:
                    # if yes
                    dataToBeInserted = []
                    # extraData to be appended with every location
                    extraData = {
                        "isActive": True,
                        "meta": {
                            "addedBy": ObjectId(req.params["kartoon-fapi-incoming"]["_id"]),
                            "addedOn": datetime.datetime.utcnow(),
                            "lastUpdatedBy": None,
                            "lastUpdatedOn": None
                        }
                    }
                    insertedIds = []
                    alreadyExists = []
                    for i in range(len(requestObj["names"])):
                        # 01. check if this location already exist
                        existingLocId = dbl.getLocationIdByName(requestObj["names"][i])
                        if not existingLocId:
                            # if not
                            dataToBeInserted.append({})
                            # 01. 01. get index for new location
                            index = dbc.getNewLocationIndex()
                            # 01. 02. increment location counter
                            dbc.incrementLocationIndex()
                            # 01. 03. prepare dataToBeInserted
                            dataToBeInserted[i]["index"] = index
                            dataToBeInserted[i]["name"] = requestObj["names"][i]
                            dataToBeInserted[i].update(extraData)
                        else:
                            # if yes
                            alreadyExists.append({
                                "_id": existingLocId,
                                "name": requestObj["names"][i]
                            })
                    if len(dataToBeInserted) > 0:
                        # 02. insert dataToBeInserted in locations
                        insertedIds = dbl.insertLocations(dataToBeInserted)
                    # 03. attach insertedIds in response
                    responseObj["data"]["_ids"] = insertedIds
                    # 04. attach alreadyExists in response
                    responseObj["data"]["alreadyExists"] = alreadyExists
                    # 05. set responseId to success
                    responseObj["responseId"] = 211
            except Exception as ex:
                responseObj["message"] = str(ex)
        resp.media = responseObj
