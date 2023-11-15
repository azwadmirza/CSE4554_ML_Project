def on_received_watch_confirmation():
    app.logger.debug(request.headers)
    if request.headers.get('X-Goog-Channel-Token') == gdrive_watch_callback_token \
            and request.headers.get('X-Goog-Resource-State') == 'change' \
            and request.data:

        data = request.data

        def updateMetaData():
            app.logger.info('Change received from gdrive')
            app.logger.debug(data)
            try:
                j = json.loads(data)
                app.logger.info('Getting change details')
                response = gdriveutils.getChangeById(gdriveutils.Gdrive.Instance().drive, j['id'])
                app.logger.debug(response)
                if response:
                    dbpath = os.path.join(config.config_calibre_dir, "metadata.db")
                    if not response['deleted'] and response['file']['title'] == 'metadata.db' and response['file']['md5Checksum'] != md5(dbpath):
                        tmpDir = tempfile.gettempdir()
                        app.logger.info('Database file updated')
                        copyfile(dbpath, os.path.join(tmpDir, "metadata.db_" + str(current_milli_time())))
                        app.logger.info('Backing up existing and downloading updated metadata.db')
                        gdriveutils.downloadFile(None, "metadata.db", os.path.join(tmpDir, "tmp_metadata.db"))
                        app.logger.info('Setting up new DB')
                        # prevent error on windows, as os.rename does on exisiting files
                        move(os.path.join(tmpDir, "tmp_metadata.db"), dbpath)
                        db.setup_db()
            except Exception as e:
                app.logger.info(e.message)
                app.logger.exception(e)
        updateMetaData()
    return ''