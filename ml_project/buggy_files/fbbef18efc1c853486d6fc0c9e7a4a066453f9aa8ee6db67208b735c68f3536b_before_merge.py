def sleep():
    # do not sleep on CI. In that case we just want to quickly test everything.
    if os.environ.get("CIRCLECI") != "true":
        time.sleep(10)