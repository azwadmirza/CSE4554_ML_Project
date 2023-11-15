def get_archive(config):
    archive = PythonPackageArchive(
        'c7n_mailer', 'ldap3', 'pyasn1', 'jinja2', 'markupsafe', 'ruamel',
        'redis', 'datadog', 'slackclient', 'requests')

    template_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'msg-templates'))

    for t in os.listdir(template_dir):
        with open(os.path.join(template_dir, t)) as fh:
            archive.add_contents('msg-templates/%s' % t, fh.read())

    archive.add_contents('config.json', json.dumps(config))
    archive.add_contents('periodic.py', entry_source)

    archive.close()
    return archive