def check_fail(module, output):
    error = [
        re.compile(r"^error", re.I)
    ]
    for x in output:
        for regex in error:
            if regex.search(x):
                module.fail_json(msg=x)