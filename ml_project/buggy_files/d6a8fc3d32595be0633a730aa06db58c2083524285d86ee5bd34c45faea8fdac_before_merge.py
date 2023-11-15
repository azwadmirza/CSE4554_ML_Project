def new_log_files(name, redirect_output):
  """Generate partially randomized filenames for log files.

  Args:
    name (str): descriptive string for this log file.
    redirect_output (bool): True if files should be generated for logging
      stdout and stderr and false if stdout and stderr should not be
      redirected.

  Returns:
    If redirect_output is true, this will return a tuple of two filehandles.
      The first is for redirecting stdout and the second is for redirecting
      stderr. If redirect_output is false, this will return a tuple of two None
      objects.
  """
  if not redirect_output:
    return None, None

  logs_dir = "/tmp/raylogs"
  if not os.path.exists(logs_dir):
    try:
      os.makedirs(logs_dir)
    except OSError as e:
      if e.errno != os.errno.EEXIST:
        raise e
      print("Attempted to create '/tmp/raylogs', but the directory already "
            "exists.")
    # Change the log directory permissions so others can use it. This is
    # important when multiple people are using the same machine.
    os.chmod(logs_dir, 0o0777)
  log_id = random.randint(0, 1000000000)
  log_stdout = "{}/{}-{:010d}.out".format(logs_dir, name, log_id)
  log_stderr = "{}/{}-{:010d}.err".format(logs_dir, name, log_id)
  log_stdout_file = open(log_stdout, "a")
  log_stderr_file = open(log_stderr, "a")
  return log_stdout_file, log_stderr_file