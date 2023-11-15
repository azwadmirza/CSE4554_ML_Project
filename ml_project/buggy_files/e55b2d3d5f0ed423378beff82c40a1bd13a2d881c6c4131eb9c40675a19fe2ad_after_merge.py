def setup_context(setup_dir):
    temp_dir = os.path.join(setup_dir, 'temp')
    with save_pkg_resources_state():
        with save_modules():
            hide_setuptools()
            with save_path():
                with save_argv():
                    with override_temp(temp_dir):
                        with pushd(setup_dir):
                            # ensure setuptools commands are available
                            if "__PEX_UNVENDORED__" in __import__("os").environ:
                              __import__('setuptools')  # vendor:skip
                            else:
                              __import__('pex.third_party.setuptools')

                            yield