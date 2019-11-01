from database.extras.destroyer import DBDestroyer

class DestroyerResource:

    def on_get(self, req, resp):
        responseObj = {}
        dbd = DBDestroyer()
        isDestroyed = dbd.destroy()
        if isDestroyed: responseObj = { "responseId": 211 }
        else: responseObj = { "responseId": 111 }
        resp.media = responseObj
