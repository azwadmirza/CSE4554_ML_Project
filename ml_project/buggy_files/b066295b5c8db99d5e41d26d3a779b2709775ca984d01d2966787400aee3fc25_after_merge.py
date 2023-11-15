    def checkout(self, element, submodule=None):
        # Element can be a tag, branch or commit
        self.check_repo()
        output = self.run('checkout "%s"' % element)
        output += self.checkout_submodules(submodule)

        return output