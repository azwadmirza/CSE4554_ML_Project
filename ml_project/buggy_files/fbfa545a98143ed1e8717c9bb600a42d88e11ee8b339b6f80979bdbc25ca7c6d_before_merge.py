    def define_routes(self):
        """
        The web app routes for receiving files
        """
        def index_logic():
            self.web.add_request(self.web.REQUEST_LOAD, request.path)

            if self.common.settings.get('public_mode'):
                upload_action = '/upload'
            else:
                upload_action = '/{}/upload'.format(self.web.slug)

            r = make_response(render_template(
                'receive.html',
                upload_action=upload_action))
            return self.web.add_security_headers(r)

        @self.web.app.route("/<slug_candidate>")
        def index(slug_candidate):
            if not self.can_upload:
                return self.web.error403()
            self.web.check_slug_candidate(slug_candidate)
            return index_logic()

        @self.web.app.route("/")
        def index_public():
            if not self.can_upload:
                return self.web.error403()
            if not self.common.settings.get('public_mode'):
                return self.web.error404()
            return index_logic()


        def upload_logic(slug_candidate=''):
            """
            Upload files.
            """
            # Make sure the receive mode dir exists
            now = datetime.now()
            date_dir = now.strftime("%Y-%m-%d")
            time_dir = now.strftime("%H.%M.%S")
            receive_mode_dir = os.path.join(self.common.settings.get('data_dir'), date_dir, time_dir)
            valid = True
            try:
                os.makedirs(receive_mode_dir, 0o700, exist_ok=True)
            except PermissionError:
                self.web.add_request(self.web.REQUEST_ERROR_DATA_DIR_CANNOT_CREATE, request.path, {
                    "receive_mode_dir": receive_mode_dir
                })
                print(strings._('error_cannot_create_data_dir').format(receive_mode_dir))
                valid = False
            if not valid:
                flash('Error uploading, please inform the OnionShare user', 'error')
                if self.common.settings.get('public_mode'):
                    return redirect('/')
                else:
                    return redirect('/{}'.format(slug_candidate))

            files = request.files.getlist('file[]')
            filenames = []
            print('')
            for f in files:
                if f.filename != '':
                    # Automatically rename the file, if a file of the same name already exists
                    filename = secure_filename(f.filename)
                    filenames.append(filename)
                    local_path = os.path.join(receive_mode_dir, filename)
                    if os.path.exists(local_path):
                        if '.' in filename:
                            # Add "-i", e.g. change "foo.txt" to "foo-2.txt"
                            parts = filename.split('.')
                            name = parts[:-1]
                            ext = parts[-1]

                            i = 2
                            valid = False
                            while not valid:
                                new_filename = '{}-{}.{}'.format('.'.join(name), i, ext)
                                local_path = os.path.join(receive_mode_dir, new_filename)
                                if os.path.exists(local_path):
                                    i += 1
                                else:
                                    valid = True
                        else:
                            # If no extension, just add "-i", e.g. change "foo" to "foo-2"
                            i = 2
                            valid = False
                            while not valid:
                                new_filename = '{}-{}'.format(filename, i)
                                local_path = os.path.join(receive_mode_dir, new_filename)
                                if os.path.exists(local_path):
                                    i += 1
                                else:
                                    valid = True

                    basename = os.path.basename(local_path)
                    if f.filename != basename:
                        # Tell the GUI that the file has changed names
                        self.web.add_request(self.web.REQUEST_UPLOAD_FILE_RENAMED, request.path, {
                            'id': request.upload_id,
                            'old_filename': f.filename,
                            'new_filename': basename
                        })

                    # Tell the GUI the receive mode directory for this file
                    self.web.add_request(self.web.REQUEST_UPLOAD_SET_DIR, request.path, {
                        'id': request.upload_id,
                        'filename': basename,
                        'dir': receive_mode_dir
                    })

                    self.common.log('ReceiveModeWeb', 'define_routes', '/upload, uploaded {}, saving to {}'.format(f.filename, local_path))
                    print(strings._('receive_mode_received_file').format(local_path))
                    f.save(local_path)

            # Note that flash strings are on English, and not translated, on purpose,
            # to avoid leaking the locale of the OnionShare user
            if len(filenames) == 0:
                flash('No files uploaded', 'info')
            else:
                for filename in filenames:
                    flash('Sent {}'.format(filename), 'info')

            if self.can_upload:
                if self.common.settings.get('public_mode'):
                    path = '/'
                else:
                    path = '/{}'.format(slug_candidate)

                return redirect('{}'.format(path))
            else:
                # It was the last upload and the timer ran out
                if self.common.settings.get('public_mode'):
                    return thankyou_logic(slug_candidate)
                else:
                    return thankyou_logic()

        def thankyou_logic(slug_candidate=''):
            r = make_response(render_template(
                'thankyou.html'))
            return self.web.add_security_headers(r)

        @self.web.app.route("/<slug_candidate>/upload", methods=['POST'])
        def upload(slug_candidate):
            if not self.can_upload:
                return self.web.error403()
            self.web.check_slug_candidate(slug_candidate)
            return upload_logic(slug_candidate)

        @self.web.app.route("/upload", methods=['POST'])
        def upload_public():
            if not self.can_upload:
                return self.web.error403()
            if not self.common.settings.get('public_mode'):
                return self.web.error404()
            return upload_logic()