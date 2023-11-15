  def LogError(self, err):
    self.logs.append("Error dumping ACPI table.")
    self.logs.append("%r: %s" % (err, err))
    self.logs.extend(self.chipsec_log.getvalue().splitlines())
    self.SendReply(chipsec_types.DumpACPITableResponse(logs=self.logs))