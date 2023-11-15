    def rm_default_view_from_shell(self, shell):
        env_mod = spack.util.environment.EnvironmentModifications()

        if default_view_name not in self.views:
            # No default view to add to shell
            return env_mod.shell_modifications(shell)

        env_mod.extend(self.unconditional_environment_modifications(
            self.default_view).reversed())

        for _, spec in self.concretized_specs():
            if spec in self.default_view and spec.package.installed:
                env_mod.extend(
                    self.environment_modifications_for_spec(
                        spec, self.default_view).reversed())
        return env_mod.shell_modifications(shell)