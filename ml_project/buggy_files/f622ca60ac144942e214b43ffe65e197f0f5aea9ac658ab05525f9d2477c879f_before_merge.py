def absent(name, **connection_args):
    """
    Ensure that the named database is absent

    name
        The name of the database to remove
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    # check if db exists and remove it
    if __salt__["mysql.db_exists"](name, **connection_args):
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "Database {0} is present and needs to be removed".format(
                name
            )
            return ret
        if __salt__["mysql.db_remove"](name, **connection_args):
            ret["comment"] = "Database {0} has been removed".format(name)
            ret["changes"][name] = "Absent"
            return ret
        else:
            err = _get_mysql_error()
            if err is not None:
                ret["comment"] = "Unable to remove database {0} " "({1})".format(
                    name, err
                )
                ret["result"] = False
                return ret
    else:
        err = _get_mysql_error()
        if err is not None:
            ret["comment"] = err
            ret["result"] = False
            return ret

    # fallback
    ret["comment"] = ("Database {0} is not present, so it cannot be removed").format(
        name
    )
    return ret