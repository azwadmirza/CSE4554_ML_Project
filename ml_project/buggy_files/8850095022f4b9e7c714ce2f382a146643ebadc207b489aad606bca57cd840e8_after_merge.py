    def check_src(item):
        if "object_id" in item:
            raise RequestParameterInvalidException("object_id not allowed to appear in the request.")

        validate_datatype_extension(datatypes_registry=trans.app.datatypes_registry, ext=item.get('ext'))

        # Normalize file:// URLs into paths.
        if item["src"] == "url" and item["url"].startswith("file://"):
            item["src"] = "path"
            item["path"] = item["url"][len("file://"):]
            del item["path"]

        if "in_place" in item:
            raise RequestParameterInvalidException("in_place cannot be set in the upload request")

        src = item["src"]

        # Check link_data_only can only be set for certain src types and certain elements_from types.
        _handle_invalid_link_data_only_elements_type(item)
        if src not in ["path", "server_dir"]:
            _handle_invalid_link_data_only_type(item)
        elements_from = item.get("elements_from", None)
        if elements_from and elements_from not in ELEMENTS_FROM_TYPE:
            raise RequestParameterInvalidException("Invalid elements_from/items_from found in request")

        if src == "path" or (src == "url" and item["url"].startswith("file:")):
            # Validate is admin, leave alone.
            validate_path_upload(trans)
        elif src == "server_dir":
            # Validate and replace with path definition.
            server_dir = item["server_dir"]
            full_path, _ = validate_server_directory_upload(trans, server_dir)
            item["src"] = "path"
            item["path"] = full_path
        elif src == "ftp_import":
            ftp_path = item["ftp_path"]
            full_path = None

            # It'd be nice if this can be de-duplicated with what is in parameters/grouping.py.
            user_ftp_dir = trans.user_ftp_dir
            is_directory = False

            assert not os.path.islink(user_ftp_dir), "User FTP directory cannot be a symbolic link"
            for (dirpath, dirnames, filenames) in os.walk(user_ftp_dir):
                for filename in filenames:
                    if ftp_path == filename:
                        path = relpath(os.path.join(dirpath, filename), user_ftp_dir)
                        if not os.path.islink(os.path.join(dirpath, filename)):
                            full_path = os.path.abspath(os.path.join(user_ftp_dir, path))
                            break

                for dirname in dirnames:
                    if ftp_path == dirname:
                        path = relpath(os.path.join(dirpath, dirname), user_ftp_dir)
                        if not os.path.islink(os.path.join(dirpath, dirname)):
                            full_path = os.path.abspath(os.path.join(user_ftp_dir, path))
                            is_directory = True
                            break

            if is_directory:
                # If the target is a directory - make sure no files under it are symbolic links
                for (dirpath, dirnames, filenames) in os.walk(full_path):
                    for filename in filenames:
                        if ftp_path == filename:
                            path = relpath(os.path.join(dirpath, filename), full_path)
                            if not os.path.islink(os.path.join(dirpath, filename)):
                                full_path = False
                                break

                    for dirname in dirnames:
                        if ftp_path == dirname:
                            path = relpath(os.path.join(dirpath, filename), full_path)
                            if not os.path.islink(os.path.join(dirpath, filename)):
                                full_path = False
                                break

            if not full_path:
                raise RequestParameterInvalidException("Failed to find referenced ftp_path or symbolic link was enountered")

            item["src"] = "path"
            item["path"] = full_path
            item["purge_source"] = purge_ftp_source
        elif src == "url":
            url = item["url"]
            looks_like_url = False
            for url_prefix in ["http://", "https://", "ftp://", "ftps://"]:
                if url.startswith(url_prefix):
                    looks_like_url = True
                    break

            if not looks_like_url:
                raise RequestParameterInvalidException("Invalid URL [%s] found in src definition." % url)

            validate_url(url, trans.app.config.fetch_url_whitelist_ips)
            item["in_place"] = run_as_real_user
        elif src == "files":
            item["in_place"] = run_as_real_user

        # Small disagreement with traditional uploads - we purge less by default since whether purging
        # happens varies based on upload options in non-obvious ways.
        # https://github.com/galaxyproject/galaxy/issues/5361
        if "purge_source" not in item:
            item["purge_source"] = False