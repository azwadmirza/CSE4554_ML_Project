  def Run(self, args):
    self.logs = []
    self.chipsec_log = StringIO.StringIO()

    if args.logging:
      self.logs.append("Dumping %s" % args.table_signature)

      logger.logger().logfile = self.chipsec_log
      logger.logger().LOG_TO_FILE = True

    # Wrap most of Chipsec code to gather its logs in case of failure.
    try:
      # Initialise Chipsec (die early if unknown chipset)
      c = chipset.cs()
      # Platform = None, Start Driver = False
      c.init(None, False)
      a = acpi.ACPI(c)

      acpi_tables_raw = a.get_ACPI_table(args.table_signature)
      acpi_tables = []

      for i, table_address in enumerate(a.tableList[args.table_signature]):
        table_header, table_content = acpi_tables_raw[i]
        table_blob = table_header + table_content

        acpi_tables.append(chipsec_types.ACPITableData(
            table_address=table_address,
            table_blob=table_blob))
    except (chipset.UnknownChipsetError, OSError) as err:
      # Expected errors that might happen on the client
      # If the chipset is unknown or we encountered an error due to reading
      # an area we do not have access to using /dev/mem, simply return an
      # error message.
      if args.logging:
        self.LogError(err)
      self.SendReply(chipsec_types.DumpACPITableResponse(logs=["%s" % err],))
      return
    except Exception as err:  # pylint: disable=broad-except
      # In case an exception is raised, if the verbose mode
      # is enabled, return the raw logs from Chipsec.
      if args.logging:
        self.LogError(err)
      raise

    if not acpi_tables:
      self.logs.append("No ACPI table with signature %s." %
                       args.table_signature)
    else:
      self.logs.append(
          "ACPI table with signature %s has been successfully dumped." %
          args.table_signature)

    if args.logging:
      self.logs.extend(self.chipsec_log.getvalue().splitlines())

    self.SendReply(chipsec_types.DumpACPITableResponse(acpi_tables=acpi_tables,
                                                       logs=self.logs))