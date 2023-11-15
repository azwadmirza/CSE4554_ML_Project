def main(argv=None, **kw):
    from pex.third_party.setuptools import setup
    from pex.third_party.setuptools.dist import Distribution

    class DistributionWithoutHelpCommands(Distribution):
        common_usage = ""

        def _show_help(self, *args, **kw):
            with _patch_usage():
                Distribution._show_help(self, *args, **kw)

    if argv is None:
        argv = sys.argv[1:]

    with _patch_usage():
        setup(
            script_args=['-q', 'easy_install', '-v'] + argv,
            script_name=sys.argv[0] or 'easy_install',
            distclass=DistributionWithoutHelpCommands,
            **kw
        )