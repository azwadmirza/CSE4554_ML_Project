def check_file_meta(
    name,
    sfn,
    source,
    source_sum,
    user,
    group,
    mode,
    attrs,
    saltenv,
    contents=None,
    seuser=None,
    serole=None,
    setype=None,
    serange=None,
):
    """
    Check for the changes in the file metadata.

    CLI Example:

    .. code-block:: bash

        salt '*' file.check_file_meta /etc/httpd/conf.d/httpd.conf salt://http/httpd.conf '{hash_type: 'md5', 'hsum': <md5sum>}' root, root, '755' base

    .. note::

        Supported hash types include sha512, sha384, sha256, sha224, sha1, and
        md5.

    name
        Path to file destination

    sfn
        Template-processed source file contents

    source
        URL to file source

    source_sum
        File checksum information as a dictionary

        .. code-block:: yaml

            {hash_type: md5, hsum: <md5sum>}

    user
        Destination file user owner

    group
        Destination file group owner

    mode
        Destination file permissions mode

    attrs
        Destination file attributes

        .. versionadded:: 2018.3.0

    saltenv
        Salt environment used to resolve source files

    contents
        File contents

    seuser
        selinux user attribute

        .. versionadded:: Sodium

    serole
        selinux role attribute

        .. versionadded:: Sodium

    setype
        selinux type attribute

        .. versionadded:: Sodium

    serange
        selinux range attribute

        .. versionadded:: Sodium
    """
    changes = {}
    if not source_sum:
        source_sum = dict()

    try:
        lstats = stats(
            name, hash_type=source_sum.get("hash_type", None), follow_symlinks=False
        )
    except CommandExecutionError:
        lstats = {}

    if not lstats:
        changes["newfile"] = name
        return changes

    if "hsum" in source_sum:
        if source_sum["hsum"] != lstats["sum"]:
            if not sfn and source:
                sfn = __salt__["cp.cache_file"](
                    source, saltenv, source_hash=source_sum["hsum"]
                )
            if sfn:
                try:
                    changes["diff"] = get_diff(
                        name, sfn, template=True, show_filenames=False
                    )
                except CommandExecutionError as exc:
                    changes["diff"] = exc.strerror
            else:
                changes["sum"] = "Checksum differs"

    if contents is not None:
        # Write a tempfile with the static contents
        if isinstance(contents, six.binary_type):
            tmp = salt.utils.files.mkstemp(
                prefix=salt.utils.files.TEMPFILE_PREFIX, text=False
            )
            with salt.utils.files.fopen(tmp, "wb") as tmp_:
                tmp_.write(contents)
        else:
            tmp = salt.utils.files.mkstemp(
                prefix=salt.utils.files.TEMPFILE_PREFIX, text=True
            )
            if salt.utils.platform.is_windows():
                contents = os.linesep.join(
                    _splitlines_preserving_trailing_newline(contents)
                )
            with salt.utils.files.fopen(tmp, "w") as tmp_:
                tmp_.write(salt.utils.stringutils.to_str(contents))
        # Compare the static contents with the named file
        try:
            differences = get_diff(name, tmp, show_filenames=False)
        except CommandExecutionError as exc:
            log.error("Failed to diff files: %s", exc)
            differences = exc.strerror
        __clean_tmp(tmp)
        if differences:
            if __salt__["config.option"]("obfuscate_templates"):
                changes["diff"] = "<Obfuscated Template>"
            else:
                changes["diff"] = differences

    if not salt.utils.platform.is_windows():
        # Check owner
        if user is not None and user != lstats["user"] and user != lstats["uid"]:
            changes["user"] = user

        # Check group
        if group is not None and group != lstats["group"] and group != lstats["gid"]:
            changes["group"] = group

        # Normalize the file mode
        smode = salt.utils.files.normalize_mode(lstats["mode"])
        mode = salt.utils.files.normalize_mode(mode)
        if mode is not None and mode != smode:
            changes["mode"] = mode

        if attrs:
            diff_attrs = _cmp_attrs(name, attrs)
            if diff_attrs is not None:
                if attrs is not None and (
                    diff_attrs[0] is not None or diff_attrs[1] is not None
                ):
                    changes["attrs"] = attrs

        # Check selinux
        if seuser or serole or setype or serange:
            try:
                (
                    current_seuser,
                    current_serole,
                    current_setype,
                    current_serange,
                ) = get_selinux_context(name).split(":")
                log.debug(
                    "Current selinux context user:{0} role:{1} type:{2} range:{3}".format(
                        current_seuser, current_serole, current_setype, current_serange
                    )
                )
            except ValueError as exc:
                log.error("Unable to get current selinux attributes")
                changes["selinux"] = exc.strerror

            if seuser and seuser != current_seuser:
                changes["selinux"] = {"user": seuser}
            if serole and serole != current_serole:
                changes["selinux"] = {"role": serole}
            if setype and setype != current_setype:
                changes["selinux"] = {"type": setype}
            if serange and serange != current_serange:
                changes["selinux"] = {"range": serange}

    return changes