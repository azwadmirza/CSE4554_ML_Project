    def runcommand(self):
        reporter.using(
            "tox-{} from {} (pid {})".format(tox.__version__, tox.__file__, os.getpid())
        )
        show_description = reporter.has_level(reporter.Verbosity.DEFAULT)
        if self.config.run_provision:
            provision_tox_venv = self.getvenv(self.config.provision_tox_env)
            return provision_tox(provision_tox_venv, self.config.args)
        else:
            if self.config.option.showconfig:
                self.showconfig()
            elif self.config.option.listenvs:
                self.showenvs(all_envs=False, description=show_description)
            elif self.config.option.listenvs_all:
                self.showenvs(all_envs=True, description=show_description)
            else:
                with self.cleanup():
                    return self.subcommand_test()