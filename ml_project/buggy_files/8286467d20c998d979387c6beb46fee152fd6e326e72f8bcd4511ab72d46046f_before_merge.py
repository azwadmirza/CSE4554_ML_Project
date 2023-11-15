    def _handle_case_conflict(self, event):
        """
        Checks for other items in the same directory with same name but a different
        case. Renames items if necessary.Only needed for case sensitive file systems.

        :param FileSystemEvent event: Created or moved event.
        :returns: ``True`` or ``False``.
        :rtype: bool
        """

        if not IS_FS_CASE_SENSITIVE:
            return False

        if event.event_type not in (EVENT_TYPE_CREATED, EVENT_TYPE_MOVED):
            return False

        # get the created path (src_path or dest_path)
        dest_path = get_dest_path(event)
        dirname, basename = osp.split(dest_path)

        # check number of paths with the same case
        if len(path_exists_case_insensitive(basename, root=dirname)) > 1:

            dest_path_cc = generate_cc_name(dest_path, suffix='case conflict')
            with self.fs_events.ignore(dest_path, recursive=osp.isdir(dest_path),
                                       event_types=(EVENT_TYPE_DELETED,
                                                    EVENT_TYPE_MOVED)):
                exc = move(dest_path, dest_path_cc)
                if exc:
                    raise os_to_maestral_error(exc, local_path=dest_path_cc)

            logger.info('Case conflict: renamed "%s" to "%s"', dest_path, dest_path_cc)

            return True
        else:
            return False