def _initialize(**kwargs):
    host = kwargs["HOST"]
    port = kwargs["PORT"]
    admin_user = kwargs["USERNAME"]
    admin_pass = kwargs["PASSWORD"]
    db_name = kwargs.get("DB_NAME", "default_db")

    if admin_user is not None and admin_pass is not None:
        url = "mongodb://{}:{}@{}:{}/{}".format(
            quote_plus(admin_user), quote_plus(admin_pass), host, port, db_name
        )
    else:
        url = "mongodb://{}:{}/{}".format(host, port, db_name)

    global _conn
    _conn = motor.motor_asyncio.AsyncIOMotorClient(url)