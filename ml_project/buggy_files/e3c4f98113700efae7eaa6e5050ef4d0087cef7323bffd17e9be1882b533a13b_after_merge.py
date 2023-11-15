  def Run(self, args):
    # Due to talking raw to hardware, this action has some inevitable risk of
    # crashing the machine, so we need to flush the transaction log to ensure
    # we know when this happens.
    self.SyncTransactionLog()

    # Temporary extra logging for Ubuntu
    # TODO(user): Add generic hunt flag to notify syslog before running each
    # client action.
    if args.notify_syslog:
      syslog = logging.getLogger("chipsec_grr")
      syslog.setLevel(logging.INFO)
      syslog.addHandler(handlers.SysLogHandler(address="/dev/log"))
      syslog.info("%s: Runnning DumpFlashImage",
                  config_lib.CONFIG["Client.name"])

    self.logs = []
    self.chipsec_log = StringIO.StringIO()

    if args.log_level:
      logger.logger().UTIL_TRACE = True
      if args.log_level == 2:
        logger.logger().VERBOSE = True
      logger.logger().logfile = self.chipsec_log
      logger.logger().LOG_TO_FILE = True

    # Create a temporary file to store the flash image.
    dest_fd, dest_pathspec = tempfiles.CreateGRRTempFileVFS()

    # Wrap most of Chipsec code to gather its logs in case of failure.
    try:
      # Initialise Chipsec (die early if unknown chipset)
      c = chipset.cs()
      # Platform = None, Start Driver = False
      c.init(None, False)
      s = spi.SPI(c)

      # Use hal.spi from chipsec to write BIOS to that file.
      with dest_fd:
        # Based on Chipsec code, rely on the address of BIOS(=1) region to
        # determine the size of the flash.
        _, limit, _ = s.get_SPI_region(1)
        spi_size = limit + 1
        # Read args.chunk_size bytes at a time and heartbeat.
        bios = []
        for i in range(0, spi_size, args.chunk_size):
          bios.extend(s.read_spi(i, args.chunk_size))
          self.Progress()
        dest_fd.write("".join(bios))

    except chipset.UnknownChipsetError as err:
      if args.log_level:
        self.LogError(err)
      tempfiles.DeleteGRRTempFile(dest_pathspec.path)
      self.SendReply(chipsec_types.DumpFlashImageResponse(logs=["%s" % err],))
      return
    except Exception as err:  # pylint: disable=broad-except
      # In case an exception is raised, if the verbose mode
      # is enabled, return the raw logs from Chipsec.
      if args.log_level:
        self.LogError(err)
      tempfiles.DeleteGRRTempFile(dest_pathspec.path)
      raise

    if args.log_level:
      self.logs.extend(self.chipsec_log.getvalue().splitlines())

    if args.notify_syslog:
      syslog.info("%s: DumpFlashImage has completed successfully",
                  config_lib.CONFIG["Client.name"])

    self.SendReply(chipsec_types.DumpFlashImageResponse(path=dest_pathspec,
                                                        logs=self.logs))