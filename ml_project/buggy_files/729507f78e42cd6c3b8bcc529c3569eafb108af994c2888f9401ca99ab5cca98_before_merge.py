    def get_path_to_ansible_inventory(self):
        venv_exe = os.path.join(self.venv_path, 'bin', 'ansible-inventory')
        if os.path.exists(venv_exe):
            return venv_exe
        return shutil.which('ansible-inventory')