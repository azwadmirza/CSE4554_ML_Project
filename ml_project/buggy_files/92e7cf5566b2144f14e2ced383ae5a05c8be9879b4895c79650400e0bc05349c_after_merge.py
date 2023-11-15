  def __init__(
      self, posix_time, call_type, user_start_call, source, destination,
      video_conference):
    """Contains information if the call was cancelled, accepted or finished.

    Args:
      posix_time: the POSIX time value, which contains the number of seconds
                  since January 1, 1970 00:00:00 UTC.
      call_type: a string containing the call type e.g. WAITING, STARTED,
                 FINISHED.
      user_start_call: a boolean which indicates that the owner account
                       started the call.
      source: a string containing the account which started the call.
      destination: a string containing the account which gets the call.
      video_conference: a boolean which indicates if the call was a video
                        conference.
    """

    super(SkypeCallEvent, self).__init__(posix_time, u'Call from Skype')
    self.call_type = call_type
    self.dst_call = destination
    self.src_call = source
    self.user_start_call = user_start_call
    self.video_conference = video_conference