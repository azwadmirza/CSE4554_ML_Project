    def __init__(self, text: base.String,
                 request_contact: base.Boolean = None,
                 request_location: base.Boolean = None,
                 request_poll: KeyboardButtonPollType = None,
                 **kwargs):
        super(KeyboardButton, self).__init__(text=text,
                                             request_contact=request_contact,
                                             request_location=request_location,
                                             request_poll=request_poll,
                                             **kwargs)