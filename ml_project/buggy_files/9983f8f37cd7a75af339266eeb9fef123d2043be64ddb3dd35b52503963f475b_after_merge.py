def get_archive(config):
    archive = PythonPackageArchive(
        'c7n_mailer',
        # core deps
        'jinja2', 'markupsafe', 'ruamel', 'ldap3', 'pyasn1', 'redis',
        # transport datadog - recursive deps
        'datadog', 'simplejson', 'decorator',
        # transport slack - recursive deps
        'slackclient', 'websocket',
        # requests (recursive deps), needed by datadog and slackclient
        'requests', 'urllib3', 'idna', 'chardet', 'certifi')

    template_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'msg-templates'))

    for t in os.listdir(template_dir):
        with open(os.path.join(template_dir, t)) as fh:
            archive.add_contents('msg-templates/%s' % t, fh.read())

    archive.add_contents('config.json', json.dumps(config))
    archive.add_contents('periodic.py', entry_source)

    archive.close()
    return archive