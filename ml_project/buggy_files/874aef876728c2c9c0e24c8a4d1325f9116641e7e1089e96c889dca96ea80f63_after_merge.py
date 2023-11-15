def write_files(journal, path, format):
    """Turns your journal into separate files for each entry.
    Format should be either json, md or txt."""
    make_filename = lambda entry: e.date.strftime("%C-%m-%d_{0}.{1}".format(slugify(u(e.title)), format))
    for e in journal.entries:
        full_path = os.path.join(path, make_filename(e))
        if format == 'json':
            content = json.dumps(e.to_dict(), indent=2) + "\n"
        elif format in ('md', 'markdown'):
            content = e.to_md()
        elif format in ('txt', 'text'):
            content = u(e)
        with codecs.open(full_path, "w", "utf-8") as f:
            f.write(content)
    return u"[Journal exported individual files in {0}]".format(path)