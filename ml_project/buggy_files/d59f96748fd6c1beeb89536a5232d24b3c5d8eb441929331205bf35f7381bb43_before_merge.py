    def _config_node(self, conanfile, conanref, down_reqs, down_ref, down_options):
        """ update settings and option in the current ConanFile, computing actual
        requirement values, cause they can be overriden by downstream requires
        param settings: dict of settings values => {"os": "windows"}
        """
        try:
            conanfile.requires.output = self._output
            if hasattr(conanfile, "config"):
                if not conanref:
                    self._output.warn("config() has been deprecated."
                                      " Use config_options and configure")
                conanfile.config()
            conanfile.config_options()
            conanfile.options.propagate_upstream(down_options, down_ref, conanref, self._output)
            if hasattr(conanfile, "config"):
                conanfile.config()
            conanfile.configure()

            conanfile.settings.validate()  # All has to be ok!
            conanfile.options.validate()

            # Update requirements (overwrites), computing new upstream
            conanfile.requirements()
            new_options = conanfile.options.values
            new_down_reqs = conanfile.requires.update(down_reqs, self._output, conanref, down_ref)
        except ConanException as e:
            raise ConanException("%s: %s" % (conanref or "Conanfile", str(e)))
        except Exception as e:
            msg = format_conanfile_exception(str(conanref or "Conanfile"),
                                             "config, config_options or configure", e)
            raise ConanException(msg)
        return new_down_reqs, new_options