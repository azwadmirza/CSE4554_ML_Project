    def __init__(self, environ, populate_request=True, shallow=False):
        super(ReceiveModeRequest, self).__init__(environ, populate_request, shallow)
        self.web = environ['web']

        # Is this a valid upload request?
        self.upload_request = False
        if self.method == 'POST':
            if self.path == '/{}/upload'.format(self.web.slug):
                self.upload_request = True
            else:
                if self.web.common.settings.get('public_mode'):
                    if self.path == '/upload':
                        self.upload_request = True

        if self.upload_request:
            # A dictionary that maps filenames to the bytes uploaded so far
            self.progress = {}

            # Create an upload_id, attach it to the request
            self.upload_id = self.upload_count
            self.upload_count += 1

            # Figure out the content length
            try:
                self.content_length = int(self.headers['Content-Length'])
            except:
                self.content_length = 0

            print("{}: {}".format(
                datetime.now().strftime("%b %d, %I:%M%p"),
                strings._("receive_mode_upload_starting").format(self.web.common.human_readable_filesize(self.content_length))
            ))

            # Tell the GUI
            self.web.add_request(self.web.REQUEST_STARTED, self.path, {
                'id': self.upload_id,
                'content_length': self.content_length
            })

            self.previous_file = None