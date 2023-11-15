def workgroup(name):
    """
    .. versionadded:: 3001

    Manage the workgroup of the computer

    Args:
        name (str): The workgroup to set

    Example:

    .. code-block:: yaml

        set workgroup:
          system.workgroup:
            - name: local
    """
    ret = {"name": name.upper(), "result": False, "changes": {}, "comment": ""}

    # Grab the current domain/workgroup
    out = __salt__["system.get_domain_workgroup"]()
    current_workgroup = (
        out["Domain"]
        if "Domain" in out
        else out["Workgroup"]
        if "Workgroup" in out
        else ""
    )

    # Notify the user if the requested workgroup is the same
    if current_workgroup.upper() == name.upper():
        ret["result"] = True
        ret["comment"] = "Workgroup is already set to '{0}'".format(name.upper())
        return ret

    # If being run in test-mode, inform the user what is supposed to happen
    if __opts__["test"]:
        ret["result"] = None
        ret["changes"] = {}
        ret["comment"] = "Computer will be joined to workgroup '{0}'".format(name)
        return ret

    # Set our new workgroup, and then immediately ask the machine what it
    # is again to validate the change
    res = __salt__["system.set_domain_workgroup"](name.upper())
    out = __salt__["system.get_domain_workgroup"]()
    new_workgroup = (
        out["Domain"]
        if "Domain" in out
        else out["Workgroup"]
        if "Workgroup" in out
        else ""
    )

    # Return our results based on the changes
    if res and current_workgroup.upper() == new_workgroup.upper():
        ret["result"] = True
        ret["comment"] = "The new workgroup '{0}' is the same as '{1}'".format(
            current_workgroup.upper(), new_workgroup.upper()
        )
    elif res:
        ret["result"] = True
        ret["comment"] = "The workgroup has been changed from '{0}' to '{1}'".format(
            current_workgroup.upper(), new_workgroup.upper()
        )
        ret["changes"] = {
            "old": current_workgroup.upper(),
            "new": new_workgroup.upper(),
        }
    else:
        ret["result"] = False
        ret["comment"] = "Unable to join the requested workgroup '{0}'".format(
            new_workgroup.upper()
        )

    return ret