  def __init__(self, timestamp, call_type, user_start_call,
               source, destination, video_conference):
    """Contains information if the call was cancelled, accepted or finished.

      Args:
        timestamp: the timestamp of the event.
        call_type: WAITING, STARTED, FINISHED.
        user_start_call: boolean, true indicates that the owner
                         account started the call.
        source: the account which started the call.
        destination: the account which gets the call.
        video_conference: boolean, if is true it was a videoconference.
    """

    super(SkypeCallEvent, self).__init__(
        timestamp, u'Call from Skype', self.DATA_TYPE)

    self.call_type = call_type
    self.user_start_call = user_start_call
    self.src_call = source
    self.dst_call = destination
    self.video_conference = video_conference