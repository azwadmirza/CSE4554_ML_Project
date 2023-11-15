    def _execute(self, options, args):
        """Given a swatch name and a parent theme, creates a custom theme."""
        if requests is None:
            utils.req_missing(['requests'], 'install Bootswatch themes')

        name = options['name']
        swatch = options['swatch']
        parent = options['parent']
        version = ''

        # See if we need bootswatch for bootstrap v2 or v3
        themes = utils.get_theme_chain(parent)
        if 'bootstrap3' not in themes:
            version = '2'
        elif 'bootstrap' not in themes:
            LOGGER.warn('"bootswatch_theme" only makes sense for themes that use bootstrap')
        elif 'bootstrap3-gradients' in themes or 'bootstrap3-gradients-jinja' in themes:
            LOGGER.warn('"bootswatch_theme" doesn\'t work well with the bootstrap3-gradients family')

        LOGGER.info("Creating '{0}' theme from '{1}' and '{2}'".format(name, swatch, parent))
        utils.makedirs(os.path.join('themes', name, 'assets', 'css'))
        for fname in ('bootstrap.min.css', 'bootstrap.css'):
            url = '/'.join(('http://bootswatch.com', version, swatch, fname))
            LOGGER.info("Downloading: " + url)
            data = requests.get(url).text
            with open(os.path.join('themes', name, 'assets', 'css', fname),
                      'wb+') as output:
                output.write(data.encode('utf-8'))

        with open(os.path.join('themes', name, 'parent'), 'wb+') as output:
            output.write(parent.encode('utf-8'))
        LOGGER.notice('Theme created.  Change the THEME setting to "{0}" to use it.'.format(name))