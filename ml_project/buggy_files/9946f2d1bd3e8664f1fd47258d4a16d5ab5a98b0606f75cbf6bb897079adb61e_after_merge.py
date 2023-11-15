    def load_extension(self, app, extname):
        # type: (Sphinx, unicode) -> None
        """Load a Sphinx extension."""
        if extname in app.extensions:  # alread loaded
            return
        if extname in EXTENSION_BLACKLIST:
            logger.warning(__('the extension %r was already merged with Sphinx since '
                              'version %s; this extension is ignored.'),
                           extname, EXTENSION_BLACKLIST[extname])
            return

        # update loading context
        app._setting_up_extension.append(extname)

        try:
            mod = __import__(extname, None, None, ['setup'])
        except ImportError as err:
            logger.verbose(__('Original exception:\n') + traceback.format_exc())
            raise ExtensionError(__('Could not import extension %s') % extname, err)

        if not hasattr(mod, 'setup'):
            logger.warning(__('extension %r has no setup() function; is it really '
                              'a Sphinx extension module?'), extname)
            metadata = {}  # type: Dict[unicode, Any]
        else:
            try:
                metadata = mod.setup(app)
            except VersionRequirementError as err:
                # add the extension name to the version required
                raise VersionRequirementError(
                    __('The %s extension used by this project needs at least '
                       'Sphinx v%s; it therefore cannot be built with this '
                       'version.') % (extname, err)
                )

        if metadata is None:
            metadata = {}
            if extname == 'rst2pdf.pdfbuilder':
                metadata['parallel_read_safe'] = True
        elif not isinstance(metadata, dict):
            logger.warning(__('extension %r returned an unsupported object from '
                              'its setup() function; it should return None or a '
                              'metadata dictionary'), extname)
            metadata = {}

        app.extensions[extname] = Extension(extname, mod, **metadata)
        app._setting_up_extension.pop()