    def on_file_renamed_alert(self, alert):
        unwanteddir_abs = os.path.join(self.get_save_path().decode('utf-8'), self.unwanted_directory_name)
        if os.path.exists(unwanteddir_abs) and all(self.handle.file_priorities()):
            shutil.rmtree(unwanteddir_abs, ignore_errors=True)