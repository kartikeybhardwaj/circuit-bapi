validate_get_overlaps_creating_pulse_schema = {
    "type": "object",
    "properties": {
        "milestoneId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
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
        },
        "members": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[0-9a-z]*$",
                "minLength": 24,
                "maxLength": 24
            },
            "minItems": 1,
            "maxItems": 20,
            "uniqueItems": True
        }
    },
    "required": [
        "milestoneId",
        "timeline",
        "members"
    ],
    "additionalProperties": False
}