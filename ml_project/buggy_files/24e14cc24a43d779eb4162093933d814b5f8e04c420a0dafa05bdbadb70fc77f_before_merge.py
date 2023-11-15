    def save_episodes_as_file(self, episodes):
        PRIVATE_FOLDER_ATTRIBUTE = '_save_episodes_as_file_folder'
        folder = getattr(self, PRIVATE_FOLDER_ATTRIBUTE, None)
        (notCancelled, folder) = self.show_folder_select_dialog(initial_directory=folder)
        setattr(self, PRIVATE_FOLDER_ATTRIBUTE, folder)

        if notCancelled:
            for episode in episodes:
                if episode.was_downloaded(and_exists=True):
                    copy_from = episode.local_filename(create=False)
                    assert copy_from is not None

                    base, extension = os.path.splitext(copy_from)
                    filename = self.build_filename(episode.sync_filename(), extension)
                    copy_to = os.path.join(folder, filename)
                    shutil.copyfile(copy_from, copy_to)