def lv_present(
    name,
    vgname=None,
    size=None,
    extents=None,
    snapshot=None,
    pv="",
    thinvolume=False,
    thinpool=False,
    force=False,
    resizefs=False,
    **kwargs
):
    """
    Ensure that a Logical Volume is present, creating it if absent.

    name
        The name of the Logical Volume

    vgname
        The name of the Volume Group on which the Logical Volume resides

    size
        The size of the Logical Volume

    extents
        The number of extents the Logical Volume
        It can be a percentage allowed by lvcreate's syntax, in this case
        it will set the Logical Volume initial size and won't be resized.

    snapshot
        The name of the snapshot

    pv
        The Physical Volume to use

    kwargs
        Any supported options to lvcreate. See
        :mod:`linux_lvm <salt.modules.linux_lvm>` for more details.

    .. versionadded:: to_complete

    thinvolume
        Logical Volume is thinly provisioned

    thinpool
        Logical Volume is a thin pool

    .. versionadded:: 2018.3.0

    force
        Assume yes to all prompts

    .. versionadded:: 3002.0

    resizefs
        Use fsadm to resize the logical volume filesystem if needed

    """
    ret = {"changes": {}, "comment": "", "name": name, "result": True}

    if extents and size:
        ret["comment"] = "Only one of extents or size can be specified."
        ret["result"] = False
        return ret

    _snapshot = None

    if snapshot:
        _snapshot = name
        name = snapshot

    if thinvolume:
        lvpath = "/dev/{}/{}".format(vgname.split("/")[0], name)
    else:
        lvpath = "/dev/{}/{}".format(vgname, name)

    lv_info = __salt__["lvm.lvdisplay"](lvpath, quiet=True)
    lv_info = lv_info.get(lvpath)

    if not lv_info:
        if __opts__["test"]:
            ret["comment"] = "Logical Volume {} is set to be created".format(name)
            ret["result"] = None
            return ret
        else:
            changes = __salt__["lvm.lvcreate"](
                name,
                vgname,
                size=size,
                extents=extents,
                snapshot=_snapshot,
                pv=pv,
                thinvolume=thinvolume,
                thinpool=thinpool,
                force=force,
                **kwargs
            )

            if __salt__["lvm.lvdisplay"](lvpath):
                ret["comment"] = "Created Logical Volume {}".format(name)
                ret["changes"]["created"] = changes
            else:
                ret["comment"] = "Failed to create Logical Volume {}. Error: {}".format(
                    name, changes["Output from lvcreate"]
                )
                ret["result"] = False
    else:
        ret["comment"] = "Logical Volume {} already present".format(name)

        if size or extents:
            old_extents = int(lv_info["Current Logical Extents Associated"])
            old_size_mb = _convert_to_mb(lv_info["Logical Volume Size"] + "s")
            if size:
                size_mb = _convert_to_mb(size)
                extents = old_extents
            else:
                # ignore percentage "extents" if the logical volume already exists
                if "%" in str(extents):
                    ret[
                        "comment"
                    ] = "Logical Volume {} already present, {} won't be resized.".format(
                        name, extents
                    )
                    extents = old_extents
                size_mb = old_size_mb

            if force is False and (size_mb < old_size_mb or extents < old_extents):
                ret[
                    "comment"
                ] = "To reduce a Logical Volume option 'force' must be True."
                ret["result"] = False
                return ret

            if size_mb != old_size_mb or extents != old_extents:
                if __opts__["test"]:
                    ret["comment"] = "Logical Volume {} is set to be resized".format(
                        name
                    )
                    ret["result"] = None
                    return ret
                else:
                    if size:
                        changes = __salt__["lvm.lvresize"](
                            lvpath=lvpath, size=size, resizefs=resizefs, force=force
                        )
                    else:
                        changes = __salt__["lvm.lvresize"](
                            lvpath=lvpath,
                            extents=extents,
                            resizefs=resizefs,
                            force=force,
                        )

                    if not changes:
                        ret[
                            "comment"
                        ] = "Failed to resize Logical Volume. Unknown Error."
                        ret["result"] = False

                    lv_info = __salt__["lvm.lvdisplay"](lvpath, quiet=True)[lvpath]
                    new_size_mb = _convert_to_mb(lv_info["Logical Volume Size"] + "s")
                    if new_size_mb != old_size_mb:
                        ret["comment"] = "Resized Logical Volume {}".format(name)
                        ret["changes"]["resized"] = changes
                    else:
                        ret[
                            "comment"
                        ] = "Failed to resize Logical Volume {}.\nError: {}".format(
                            name, changes["Output from lvresize"]
                        )
                        ret["result"] = False
    return ret