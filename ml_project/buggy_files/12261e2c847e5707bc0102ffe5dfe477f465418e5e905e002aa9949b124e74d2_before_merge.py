def wait_on_exit(container):
    exit_code = container.wait()
    return "%s exited with code %s\n" % (container.name, exit_code)