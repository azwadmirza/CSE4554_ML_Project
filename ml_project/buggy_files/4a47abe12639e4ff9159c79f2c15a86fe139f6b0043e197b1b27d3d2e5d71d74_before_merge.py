def execute_link(link_cmd_args, record_streams):
  """
  <Purpose>
    Executes the passed command plus arguments in a subprocess and returns
    the return value of the executed command. If the specified standard output
    and standard error of the command are recorded and also returned to the
    caller.

  <Arguments>
    link_cmd_args:
            A list where the first element is a command and the remaining
            elements are arguments passed to that command.
    record_streams:
            A bool that specifies whether to redirect standard output and
            and standard error to a temporary file which is returned to the
            caller (True) or not (False).

  <Exceptions>
    TBA (see https://github.com/in-toto/in-toto/issues/6)

  <Side Effects>
    Executes passed command in a subprocess and redirects stdout and stderr
    if specified.

  <Returns>
    - A dictionary containing standard output and standard error of the
      executed command, called by-products.
      Note: If record_streams is False, the dict values are empty strings.
    - The return value of the executed command.
  """
  if record_streams:
    return_code, stdout_str, stderr_str = \
        in_toto.process.run_duplicate_streams(link_cmd_args)

  else:
    process = in_toto.process.run(link_cmd_args, check=False,
      stdout=in_toto.process.DEVNULL, stderr=in_toto.process.DEVNULL)
    stdout_str = stderr_str = ""
    return_code = process.returncode

  return {
      "stdout": stdout_str,
      "stderr": stderr_str,
      "return-value": return_code
    }