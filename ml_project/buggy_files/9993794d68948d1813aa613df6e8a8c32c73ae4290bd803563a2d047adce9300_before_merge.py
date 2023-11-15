def item_file(item_id):
    item = g.lib.get_item(item_id)
    response = flask.send_file(
        util.py3_path(item.path),
        as_attachment=True,
        attachment_filename=os.path.basename(util.py3_path(item.path)),
    )
    response.headers['Content-Length'] = os.path.getsize(item.path)
    return response