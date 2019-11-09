validate_add_meta_project_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "pattern": "^[0-9a-zA-Z\-\ ]*$",
            "minLength": 4,
            "maxLength": 20
        },
        "description": {
            "type": "string",
            "minLength": 4,
            "maxLength": 40
        },
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\-\ ]*$",
                        "minLength": 4,
                        "maxLength": 20
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
                            "maxLength": 20
                        }, {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "pattern": "^[0-9a-zA-Z\-\ ]*$",
                                "minLength": 1,
                                "maxLength": 20
                            },
                            "minItems": 1,
                            "maxItems": 5,
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
            "maxItems": 5,
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
