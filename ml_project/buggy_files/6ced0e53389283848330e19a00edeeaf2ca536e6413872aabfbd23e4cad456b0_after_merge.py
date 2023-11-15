  def __init__(self, posix_time, phone_number, text):
    """Read the information related with the SMS.

    Args:
      posix_time: the POSIX time value, which contains the number of seconds
                  since January 1, 1970 00:00:00 UTC.
      phone_number: a string containing the phone number where the SMS was sent.
      text: a string containing the text (SMS body) that was sent.
    """
    super(SkypeSMSEvent, self).__init__(posix_time, u'SMS from Skype')
    self.number = phone_number
    self.text = text