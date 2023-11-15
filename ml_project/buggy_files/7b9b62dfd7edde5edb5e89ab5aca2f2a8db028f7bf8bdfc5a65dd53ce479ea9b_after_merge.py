    def __init__(self, environ, populate_request=True, shallow=False):
        super(ReceiveModeRequest, self).__init__(environ, populate_request, shallow)
        self.web = environ['web']
        self.stop_q = environ['stop_q']

        self.web.common.log('ReceiveModeRequest', '__init__')

        # Prevent running the close() method more than once
        self.closed = False

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

            # Prevent new uploads if we've said so (timer expired)
            if self.web.receive_mode.can_upload:

                # Create an upload_id, attach it to the request
                self.upload_id = self.web.receive_mode.upload_count

                self.web.receive_mode.upload_count += 1

               # Figure out the content length
                try:
                    self.content_length = int(self.headers['Content-Length'])
                except:
                    self.content_length = 0

                print("{}: {}".format(
                    datetime.now().strftime("%b %d, %I:%M%p"),
                    strings._("receive_mode_upload_starting").format(self.web.common.human_readable_filesize(self.content_length))
                ))

                # Don't tell the GUI that a request has started until we start receiving files
                self.told_gui_about_request = False

                self.previous_file = None