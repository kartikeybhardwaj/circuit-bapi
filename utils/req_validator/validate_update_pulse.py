validate_update_pulse_schema = {
    "type": "object",
    "properties": {
        "projectId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        },
        "milestoneId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        },
        "pulseId": {
            "type": "string",
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        },
        "title": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\-\ ]*$",
            "minLength": 2,
            "maxLength": 200
        },
        "description": {
            "type": "string",
            "minLength": 4,
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
        },
        "color": {
            "type": "string",
            "enum": [
                "blue",
                "green",
                "red",
                "black"
            ]
        },
        "assignees": {
            "type": "array",
            "minItems": 0,
            "maxItems": 50,
            "uniqueItems": True,
            "items": {
                "type": "string",
                "pattern": "^[0-9a-z]*$",
                "minLength": 24,
                "maxLength": 24
            }
        },
        "assigneesTodo": {
            "type": "object",
            "properties": {
                "toAdd": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 50,
                    "uniqueItems": True,
                    "items": {
                        "type": "string",
                        "pattern": "^[0-9a-z]*$",
                        "minLength": 24,
                        "maxLength": 24
                    }
                },
                "toRemove": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 50,
                    "uniqueItems": True,
                    "items": {
                        "type": "string",
                        "pattern": "^[0-9a-z]*$",
                        "minLength": 24,
                        "maxLength": 24
                    }
                }
            },
            "required": [
                "toAdd",
                "toRemove"
            ],
            "additionalProperties": False
        },
        "pulseMetaId": {
            "type": [
                "string",
                "null"
            ],
            "pattern": "^[0-9a-z]*$",
            "minLength": 24,
            "maxLength": 24
        },
        "fields": {
            "type": "array",
            "minItems": 0,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "minLength": 1
                    },
                    "value": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": [
                    "key",
                    "value"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": [
        "projectId",
        "milestoneId",
        "pulseId",
        "title",
        "description",
        "timeline",
        "color",
        "assignees",
        "assigneesTodo",
        "pulseMetaId",
        "fields"
    ]
}
