def _execute(command):
    proc = Popen(command, shell=True, bufsize=1, stdout=PIPE, stderr=STDOUT)

    output_buffer = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        # output.write(line)
        output_buffer.append(str(line))

    proc.communicate()
    return proc.returncode, "".join(output_buffer)