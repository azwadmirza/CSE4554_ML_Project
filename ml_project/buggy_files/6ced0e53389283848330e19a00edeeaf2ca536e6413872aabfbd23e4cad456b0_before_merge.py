  def __init__(self, row, dst_number):
    """Read the information related with the SMS.

      Args:
        row: row form the sql query.
          row['time_sms']: timestamp when the sms was send.
          row['dstnum_sms']: number which receives the sms.
          row['msg_sms']: text send to this sms.
        dst_number: phone number where the user send the sms.
    """
    # Note that pysqlite does not accept a Unicode string in row['string'] and
    # will raise "IndexError: Index must be int or string".

    super(SkypeSMSEvent, self).__init__(
        row['time_sms'], u'SMS from Skype', self.DATA_TYPE)

    self.number = dst_number
    self.text = row['msg_sms']