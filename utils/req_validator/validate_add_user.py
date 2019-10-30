validate_add_user_schema = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\.\_]*$",
            "minLength": 4,
            "maxLength": 20
        },
        "displayname": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\.\_\ ]*$",
            "minLength": 4,
            "maxLength": 20
        }
    },
    "required": [
        "username",
        "displayname"
    ],
    "additionalProperties": False
}
