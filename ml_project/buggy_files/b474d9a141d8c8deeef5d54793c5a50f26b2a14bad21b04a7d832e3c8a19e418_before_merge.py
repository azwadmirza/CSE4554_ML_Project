def present(name, character_set=None, collate=None, **connection_args):
    """
    Ensure that the named database is present with the specified properties

    name
        The name of the database to manage
    """
    ret = {
        "name": name,
        "changes": {},
        "result": True,
        "comment": "Database {0} is already present".format(name),
    }
    # check if database exists
    existing = __salt__["mysql.db_get"](name, **connection_args)
    if existing:
        alter = False
        if character_set and character_set != existing.get("character_set"):
            log.debug(
                "character set differes from %s : %s",
                character_set,
                existing.get("character_set"),
            )
            alter = True
        if collate and collate != existing.get("collate"):
            log.debug(
                "collate set differs from %s : %s", collate, existing.get("collate")
            )
            alter = True
        if alter:
            __salt__["mysql.alter_db"](
                name, character_set=character_set, collate=collate, **connection_args
            )
        current = __salt__["mysql.db_get"](name, **connection_args)
        if existing.get("collate", None) != current.get("collate", None):
            ret["changes"].update(
                {
                    "collate": {
                        "before": existing.get("collate", None),
                        "now": current.get("collate", None),
                    }
                }
            )
        if existing.get("character_set", None) != current.get("character_set", None):
            ret["changes"].update(
                {
                    "character_set": {
                        "before": existing.get("character_set", None),
                        "now": current.get("character_set", None),
                    }
                }
            )
        return ret
    else:
        err = _get_mysql_error()
        if err is not None:
            ret["comment"] = err
            ret["result"] = False
            return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = ("Database {0} is not present and needs to be created").format(
            name
        )
        return ret
    # The database is not present, make it!
    if __salt__["mysql.db_create"](
        name, character_set=character_set, collate=collate, **connection_args
    ):
        ret["comment"] = "The database {0} has been created".format(name)
        ret["changes"][name] = "Present"
    else:
        ret["comment"] = "Failed to create database {0}".format(name)
        err = _get_mysql_error()
        if err is not None:
            ret["comment"] += " ({0})".format(err)
        ret["result"] = False

    return ret