validate_add_non_availability_schema = {
    "type": "object",
    "properties": {
        "reason": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\.\_\ ]*$",
            "minLength": 2,
            "maxLength": 400
        },
        "timeline": {
            "type": "object",
            "properties": {
                "begin": {
                    "type": "string",
                    "pattern": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z"
                },
                "end": {
                    "type": "string",
                    "pattern": "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z"
                }
            },
            "required": [
                "begin",
                "end"
            ],
            "additionalProperties": False
        }
    },
    "required": [
        "reason",
        "timeline"
    ],
    "additionalProperties": False
}