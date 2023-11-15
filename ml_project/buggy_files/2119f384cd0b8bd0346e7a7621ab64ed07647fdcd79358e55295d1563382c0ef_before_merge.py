  def __init__(
      self, timestamp, usage, identifier, full_name, display_name, email,
      country):
    """Initialize the event.

    Args:
      timestamp: The POSIX timestamp value.
      usage: A string containing the description string of the timestamp.
      identifier: The row identifier.
      full_name: A string containing the full name of the Skype account holder.
      display_name: A string containing the chosen display name of the account
                    holder.
      email: A string containing the registered email address of the account
             holder.
      country: A string containing the chosen home country of the account
               holder.
    """
    super(SkypeAccountEvent, self).__init__(timestamp, usage)

    self.offset = identifier
    self.username = u'{0:s} <{1:s}>'.format(full_name, display_name)
    self.display_name = display_name
    self.email = email
    self.country = country
    self.data_type = self.DATA_TYPE