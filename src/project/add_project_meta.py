from bson.objectid import ObjectId
import datetime
import re

from database.counter.counter import DBCounter
from database.project.project import DBProject

class AddProjectMetaResource:

    def on_post(self, req, resp):
        responseObj = {
            "responseId": 111,
            "message": "",
            "data": {}
        }
        try:
            requestObj = req.media

        except Exception as ex:
            responseObj["message"] = str(ex)
        resp.media = responseObj
