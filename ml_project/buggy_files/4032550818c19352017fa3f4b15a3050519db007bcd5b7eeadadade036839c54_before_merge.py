    def _create_connect_string(param):
        """
        create the connectstring

        Port, Password, conParams, Driver, User,
        Server, Database
        """
        port = ""
        password = ""
        conParams = ""
        if param.get("Port"):
            port = ":{0!s}".format(param.get("Port"))
        if param.get("Password"):
            password = ":{0!s}".format(param.get("Password"))
        if param.get("conParams"):
            conParams = "?{0!s}".format(param.get("conParams"))
        connect_string = "{0!s}://{1!s}{2!s}{3!s}{4!s}{5!s}/{6!s}{7!s}".format(param.get("Driver", ""),
                                                   param.get("User", ""),
                                                   password,
                                                   "@" if (param.get("User")
                                                           or
                                                           password) else "",
                                                   param.get("Server", ""),
                                                   port,
                                                   param.get("Database", ""),
                                                   conParams)
        # SQLAlchemy does not like a unicode connect string!
        if param.get("Driver").lower() == "sqlite":
            connect_string = str(connect_string)
        return connect_string