import datetime

class Utils:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getDateFromUTCString(self, date: str) -> "datetime.datetime":
        return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
