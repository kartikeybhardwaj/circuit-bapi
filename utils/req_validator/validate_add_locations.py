validate_add_locations_schema = {
    "type": "object",
    "properties": {
        "names": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\-\.\ ]*$",
                        "minLength": 2,
                        "maxLength": 200
                    },
                    "country": {
                        "type": "string",
                        "pattern": "^[0-9a-zA-Z\-\.\ ]*$",
                        "minLength": 2,
                        "maxLength": 200
                    }
                },
                "required": [
                    "city",
                    "country"
                ],
                "additionalProperties": False
            },
            "minItems": 1,
            "maxItems": 20,
            "uniqueItems": True
        }
    },
    "required": [
        "names"
    ],
    "additionalProperties": False
}
