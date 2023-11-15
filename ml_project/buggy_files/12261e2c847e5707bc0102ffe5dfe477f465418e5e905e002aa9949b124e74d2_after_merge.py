def wait_on_exit(container):
    try:
        exit_code = container.wait()
        return "%s exited with code %s\n" % (container.name, exit_code)
    except APIError as e:
        return "Unexpected API error for %s (HTTP code %s)\nResponse body:\n%s\n" % (
            container.name, e.response.status_code,
            e.response.text or '[empty]'
        )