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

  # Create a directory to be used for process log files.
  logs_dir = "/tmp/raylogs"
  try_to_create_directory(logs_dir)
  # Create another directory that will be used by some of the RL algorithms.
  try_to_create_directory("/tmp/ray")

  log_id = random.randint(0, 1000000000)
  log_stdout = "{}/{}-{:010d}.out".format(logs_dir, name, log_id)
  log_stderr = "{}/{}-{:010d}.err".format(logs_dir, name, log_id)
  log_stdout_file = open(log_stdout, "a")
  log_stderr_file = open(log_stderr, "a")
  return log_stdout_file, log_stderr_file