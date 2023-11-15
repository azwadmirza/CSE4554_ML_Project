    def dlconfig_changed_callback(self, section, name, new_value, old_value):
        if section == 'downloadconfig' and name == 'max_upload_rate':
            self.handle.set_upload_limit(int(new_value * 1024))
        elif section == 'downloadconfig' and name == 'max_download_rate':
            self.handle.set_download_limit(int(new_value * 1024))
        elif section == 'downloadconfig' and name in ['correctedfilename', 'super_seeder']:
            return False
        return True