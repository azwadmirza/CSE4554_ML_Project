def bkapp_page():
    script = autoload_server(model=None, url='http://localhost:5006/bkapp')
    return render_template("embed.html", script=script)