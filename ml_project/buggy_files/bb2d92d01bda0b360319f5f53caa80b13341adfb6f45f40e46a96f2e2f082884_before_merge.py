    def massStoreRun(self, name, version, b64zip, force):
        self.__require_store()
        # Unzip sent data.
        zip_dir = unzip(b64zip)

        LOG.debug("Using unzipped folder '{0}'".format(zip_dir))

        source_root = os.path.join(zip_dir, 'root')
        report_dir = os.path.join(zip_dir, 'reports')
        metadata_file = os.path.join(report_dir, 'metadata.json')
        content_hash_file = os.path.join(zip_dir, 'content_hashes.json')

        with open(content_hash_file) as chash_file:
            filename2hash = json.load(chash_file)

        check_commands, check_durations, skip_handlers = \
            store_handler.metadata_info(metadata_file)

        if len(check_commands) == 0:
            command = ' '.join(sys.argv)
        elif len(check_commands) == 1:
            command = ' '.join(check_commands[0])
        else:
            command = "multiple analyze calls: " + \
                      '; '.join([' '.join(com) for com in check_commands])

        # Storing file contents from plist.
        file_path_to_id = {}

        _, _, report_files = next(os.walk(report_dir), ([], [], []))
        for f in report_files:
            if not f.endswith('.plist'):
                continue

            LOG.debug("Parsing input file '" + f + "'")

            try:
                files, _ = plist_parser.parse_plist(
                    os.path.join(report_dir, f))
            except Exception as ex:
                LOG.error('Parsing the plist failed: ' + str(ex))
                continue

            for file_name in files:
                source_file_name = os.path.join(source_root,
                                                file_name.strip("/"))
                LOG.debug("Storing source file:"+source_file_name)

                if not os.path.isfile(source_file_name):
                    # The file was not in the ZIP file,
                    # because we already have the content.
                    # Let's check if we already have a
                    # file record in the database or we need to
                    # add one.

                    LOG.debug(file_name + ' not found or already stored.')
                    fid = store_handler.addFileRecord(self.__Session(),
                                                      file_name,
                                                      filename2hash[file_name])
                    if not fid:
                        LOG.error("File ID for " + source_file_name +
                                  "is not found in the DB with content hash " +
                                  filename2hash[file_name] +
                                  ". Missing from ZIP?")
                    file_path_to_id[file_name] = fid
                    LOG.debug(str(fid) + " fileid found")
                    continue

                with codecs.open(source_file_name, 'r',
                                 'UTF-8', 'replace') as source_file:
                    file_content = source_file.read()
                    # TODO: we may not use the file content in the end
                    # depending on skippaths.
                    file_content = codecs.encode(file_content, 'utf-8')

                    file_path_to_id[file_name] = \
                        store_handler.addFileContent(self.__Session(),
                                                     file_name,
                                                     file_content,
                                                     None)

        run_id = store_handler.addCheckerRun(self.__Session(),
                                             self.__storage_session,
                                             command,
                                             name,
                                             version,
                                             force)

        session = self.__storage_session.get_transaction(run_id)

        # Handle skip list.
        for skip_handler in skip_handlers:
            if not store_handler.addSkipPath(self.__storage_session,
                                             run_id,
                                             skip_handler.get_skiplist()):
                LOG.debug("Adding skip path failed!")

        # Processing PList files.
        _, _, report_files = next(os.walk(report_dir), ([], [], []))
        for f in report_files:
            if not f.endswith('.plist'):
                continue

            LOG.debug("Parsing input file '" + f + "'")

            try:
                # FIXME: We are parsing the plists for the
                # second time here. Use re-use the
                # previous results.
                files, reports = plist_parser.parse_plist(
                    os.path.join(report_dir, f))
            except Exception as ex:
                LOG.error('Parsing the plist failed: ' + str(ex))
                continue

            file_ids = OrderedDict()
            # Store content of file to the server if needed.
            for file_name in files:
                file_ids[file_name] = file_path_to_id[file_name]

            # Store report.
            for report in reports:
                LOG.debug("Storing check results to the database.")

                checker_name = report.main['check_name']
                context = generic_package_context.get_context()
                severity_name = context.severity_map.get(checker_name,
                                                         'UNSPECIFIED')
                severity = \
                    shared.ttypes.Severity._NAMES_TO_VALUES[severity_name]

                bug_paths, bug_events = \
                    store_handler.collect_paths_events(report, file_ids)

                LOG.debug("Storing report")
                report_id = store_handler.addReport(
                    self.__storage_session,
                    run_id,
                    file_ids[files[report.main['location']['file']]],
                    report.main,
                    bug_paths,
                    bug_events,
                    checker_name,
                    severity)

                last_report_event = report.bug_path[-1]
                sp_handler = suppress_handler.SourceSuppressHandler(
                    files[last_report_event['location']['file']],
                    last_report_event['location']['line'],
                    report.main['issue_hash_content_of_line_in_context'],
                    report.main['check_name'])

                supp = sp_handler.get_suppressed()
                if supp:
                    bhash, fname, comment = supp
                    status = shared.ttypes.ReviewStatus.FALSE_POSITIVE
                    self._setReviewStatus(report_id, status, comment, session)

                LOG.debug("Storing done for report " + str(report_id))

        if len(check_durations) > 0:
            store_handler.setRunDuration(self.__storage_session,
                                         run_id,
                                         # Round the duration to seconds.
                                         int(sum(check_durations)))

        store_handler.finishCheckerRun(self.__storage_session, run_id)

        # TODO: This directory should be removed even if an exception is thrown
        # above.
        shutil.rmtree(zip_dir)

        return run_id