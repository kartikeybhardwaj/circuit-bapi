validate_get_user_pulses_schema = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\.\_]*$",
            "minLength": 4,
            "maxLength": 200
        }
    },
    "required": [
        "username"
    ]
}
