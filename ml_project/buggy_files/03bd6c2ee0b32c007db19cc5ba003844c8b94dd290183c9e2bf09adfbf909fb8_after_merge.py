    def add_folder(self, folder):
        self.copier(self.system_stdlib / folder, self.stdlib / folder)