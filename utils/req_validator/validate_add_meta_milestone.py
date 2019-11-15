validate_add_meta_milestone_schema = {
    "type": "object",
    "properties": {
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
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\-\ ]*$",
                        "minLength": 2,
                        "maxLength": 200
                    },
                    "valueType": {
                        "type": "string",
                        "enum": [
                            "input",
                            "select"
                        ]
                    },
                    "value": {
                        "anyOf": [{
                            "type": "string",
                            "pattern": "^[0-9a-zA-Z\-\ ]*$",
                            "minLength": 0,
                            "maxLength": 200
                        }, {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "pattern": "^[0-9a-zA-Z\-\ ]*$",
                                "minLength": 1,
                                "maxLength": 200
                            },
                            "minItems": 1,
                            "maxItems": 20,
                            "uniqueItems": True
                        }]
                    }
                },
                "required": [
                    "key",
                    "valueType",
                    "value"
                ],
                "additionalProperties": False
            },
            "minItems": 1,
            "maxItems": 10,
            "uniqueItems": True
        }
    },
    "required": [
        "title",
        "description",
        "fields"
    ],
    "additionalProperties": False
}
