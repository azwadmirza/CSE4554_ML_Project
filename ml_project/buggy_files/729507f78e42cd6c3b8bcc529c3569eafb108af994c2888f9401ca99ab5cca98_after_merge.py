    def get_path_to_ansible_inventory(self):
        venv_exe = os.path.join(self.venv_path, 'bin', 'ansible-inventory')
        if os.path.exists(venv_exe):
            return venv_exe
        elif os.path.exists(
            os.path.join(self.venv_path, 'bin', 'ansible')
        ):
            # if bin/ansible exists but bin/ansible-inventory doesn't, it's
            # probably a really old version of ansible that doesn't support
            # ansible-inventory
            raise RuntimeError(
                "{} does not exist (please upgrade to ansible >= 2.4)".format(
                    venv_exe
                )
            )
        return shutil.which('ansible-inventory')