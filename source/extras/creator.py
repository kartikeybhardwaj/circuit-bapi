from database.extras.creator import DBCreator

class CreatorResource:

    def on_get(self, req, resp):
        responseObj = {}
        dbc = DBCreator()
        isCreated = dbc.create()
        if isCreated: responseObj = { "responseId": 211 }
        else: responseObj = { "responseId": 111 }
        resp.media = responseObj
