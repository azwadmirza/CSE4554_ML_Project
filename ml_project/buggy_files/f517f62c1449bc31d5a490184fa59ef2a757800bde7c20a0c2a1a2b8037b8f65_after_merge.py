  def exit_and_fail(self, msg=None, out=None):
    """Exits the runtime with a nonzero exit code, indicating failure.

    :param msg: A string message to print to stderr or another custom file desciptor before exiting.
                (Optional)
    :param out: The file descriptor to emit `msg` to. (Optional)
    """
    self.exit(result=PANTS_FAILED_EXIT_CODE, msg=msg, out=out)