db.createUser(
    {
        user: 'user',
        pwd: 'p4ss',
        roles: [
            {
                role: 'readWrite',
                db: 'circuit'
            },
            {
                role: 'dbAdmin',
                db: 'circuit'
            }
        ]
    }
)