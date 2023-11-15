    def create(cls, path):
        # type: (str) -> Pip
        """Creates a pip tool with PEX isolation at path.

        :param path: The path to build the pip tool pex at.
        """
        pip_pex_path = os.path.join(path, isolated().pex_hash)
        with atomic_directory(pip_pex_path, exclusive=True) as chroot:
            if chroot is not None:
                from pex.pex_builder import PEXBuilder

                isolated_pip_builder = PEXBuilder(path=chroot)
                pythonpath = third_party.expose(["pip", "setuptools", "wheel"])
                isolated_pip_environment = third_party.pkg_resources.Environment(
                    search_path=pythonpath
                )
                for dist_name in isolated_pip_environment:
                    for dist in isolated_pip_environment[dist_name]:
                        isolated_pip_builder.add_dist_location(dist=dist.location)
                with open(os.path.join(isolated_pip_builder.path(), "run_pip.py"), "w") as fp:
                    fp.write(
                        dedent(
                            """\
                            import os
                            import runpy
                            import sys
                            
                            
                            # Propagate un-vendored setuptools to pip for any legacy setup.py builds it needs to
                            # perform.
                            os.environ['__PEX_UNVENDORED__'] = '1'
                            os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)
                            
                            runpy.run_module('pip', run_name='__main__')
                            """
                        )
                    )
                isolated_pip_builder.set_executable(fp.name)
                isolated_pip_builder.freeze()

        return cls(pip_pex_path)