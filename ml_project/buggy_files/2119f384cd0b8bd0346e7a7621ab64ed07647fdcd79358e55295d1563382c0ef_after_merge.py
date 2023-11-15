  def __init__(
      self, posix_time, usage, identifier, full_name, display_name, email,
      country):
    """Initialize the event.

    Args:
      posix_time: the POSIX time value, which contains the number of seconds
                  since January 1, 1970 00:00:00 UTC.
      usage: a string containing the description string of the timestamp.
      identifier: an integer containing the row identifier.
      full_name: a string containing the full name of the Skype account holder.
      display_name: a string containing the chosen display name of the account
                    holder.
      email: a string containing the registered email address of the account
             holder.
      country: a string containing the chosen home country of the account
               holder.
    """
    super(SkypeAccountEvent, self).__init__(posix_time, usage)
    self.country = country
    self.display_name = display_name
    self.email = email
    self.offset = identifier
    self.username = u'{0:s} <{1:s}>'.format(full_name, display_name)