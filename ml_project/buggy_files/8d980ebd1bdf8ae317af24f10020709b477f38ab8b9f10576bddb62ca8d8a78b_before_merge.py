    def get_files_completion(self):
        """ Returns a list of filename, progress tuples indicating the progress
        for every file selected using set_selected_files. Progress is a float
        between 0 and 1
        """
        completion = []

        if self.lt_status:
            try:
                files = self.download.handle.get_torrent_info().files()
            except RuntimeError:
                # If we don't have the torrent file yet, we'll get a runtime error
                # stating that we used an invalid handle
                files = []

            for index, byte_progress in enumerate(self.download.handle.file_progress(flags=1)):
                current_file = files[index]
                completion.append((current_file.path, float(byte_progress) / current_file.size))

        return completion