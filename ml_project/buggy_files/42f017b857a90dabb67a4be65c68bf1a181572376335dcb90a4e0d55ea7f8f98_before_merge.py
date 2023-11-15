def open_browser():
    # Child process
    time.sleep(0.5)
    webbrowser.open("http://localhost:%d/en/latest/index.html" % PORT, new="tab")