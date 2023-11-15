    def checkout(self, element, submodule=None):
        self.check_repo()
        output = self.run('checkout "%s"' % element)

        if submodule:
            if submodule == "shallow":
                output += self.run("submodule sync")
                output += self.run("submodule update --init")
            elif submodule == "recursive":
                output += self.run("submodule sync --recursive")
                output += self.run("submodule update --init --recursive")
            else:
                raise ConanException("Invalid 'submodule' attribute value in the 'scm'. "
                                     "Unknown value '%s'. Allowed values: ['shallow', 'recursive']"
                                     % submodule)
        # Element can be a tag, branch or commit
        return output