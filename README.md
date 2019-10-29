# Circuit Backend API

### pip3 install falcon
### pip3 install falcon-cors
### pip3 install pymongo
### pip3 install pyjwt
### pip3 install jsonschema
### pip3 install gunicorn

### gunicorn -b localhost:3200 app:api
### gunicorn -b localhost:3200 app:api --reload
### gunicorn -b localhost:3200 app:api --daemon
### gunicorn -b localhost:3200 app:api --daemon --reload

```
mongod --dbpath "<PATH_LOCATION_HERE>"
```

```
mongo
use circuit;
```

```
db.createUser({
	"user": "kart",
	"pwd": "oon",
	"roles": ["readWrite", "dbAdmin"]
});
```

```
mongo "mongodb://kart:oon@127.0.0.1:27017/circuit"
```

## RESPONSE IDs

```
211 - All Success
111 - Unknown Failure
110 - Validation Failure, check message
109 - Unauthorized access
```