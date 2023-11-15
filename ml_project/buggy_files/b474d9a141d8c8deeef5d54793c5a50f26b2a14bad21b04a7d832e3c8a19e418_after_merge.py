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
        "comment": "Database {} is already present".format(name),
    }
    # check if database exists
    existing = __salt__["mysql.db_get"](name, **connection_args)
    if existing:
        alter_charset = False
        alter_collate = False
        existing_charset = bytes(str(existing.get("character_set")).encode()).decode()
        if character_set and character_set != existing_charset:
            alter_charset = True
            log.debug(
                "character set differes from %s : %s", character_set, existing_charset,
            )

            comment = ("Database character set {} != {} needs to be updated").format(
                character_set, existing_charset
            )
            if __opts__.get("test", False):
                ret["result"] = None
                ret["comment"] = comment
            else:
                ret["comment"] = comment

        existing_collate = bytes(str(existing.get("collate")).encode()).decode()
        if collate and collate != existing_collate:
            alter_collate = True
            log.debug(
                "collate set differs from %s : %s", collate, existing_collate,
            )

            comment = ("Database collate {} != {} needs to be updated").format(
                collate, existing_collate
            )
            if __opts__.get("test", False):
                ret["result"] = None
                ret["comment"] += "\n{}".format(comment)
                return ret
            else:
                ret["comment"] += "\n{}".format(comment)

        if alter_charset or alter_collate:
            if __opts__.get("test", False):
                ret["comment"] += "\nDatabase {} is going to be updated".format(name)
            else:
                __salt__["mysql.alter_db"](
                    name,
                    character_set=character_set,
                    collate=collate,
                    **connection_args
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

    if __opts__.get("test", False):
        ret["result"] = None
        ret["comment"] = ("Database {} is not present and needs to be created").format(
            name
        )
        return ret

    # The database is not present, make it!
    if __salt__["mysql.db_create"](
        name, character_set=character_set, collate=collate, **connection_args
    ):
        ret["comment"] = "The database {} has been created".format(name)
        ret["changes"][name] = "Present"
    else:
        ret["comment"] = "Failed to create database {}".format(name)
        err = _get_mysql_error()
        if err is not None:
            ret["comment"] += " ({})".format(err)
        ret["result"] = False

    return ret