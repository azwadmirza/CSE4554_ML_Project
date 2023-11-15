def item_file(item_id):
    item = g.lib.get_item(item_id)
    item_path = util.syspath(item.path) if (os.name == 'nt') else (
        util.py3_path(item.path))
    response = flask.send_file(
        item_path,
        as_attachment=True,
        attachment_filename=os.path.basename(util.py3_path(item.path)),
    )
    response.headers['Content-Length'] = os.path.getsize(item_path)
    return response