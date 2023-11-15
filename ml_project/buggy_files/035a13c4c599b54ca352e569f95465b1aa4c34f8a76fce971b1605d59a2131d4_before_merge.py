    def list_associated_files(self, file_path, base_name_only=False,  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
                              subtitles_only=False, subfolders=False):  # pylint: disable=unused-argument
        """
        For a given file path searches for files with the same name but different extension and returns their absolute paths

        :param file_path: The file to check for associated files

        :param base_name_only: False add extra '.' (conservative search) to file_path minus extension

        :return: A list containing all files which are associated to the given file
        """
        def recursive_glob(treeroot, pattern):
            results = []
            for base, _, files in ek(os.walk, treeroot.encode(sickbeard.SYS_ENCODING)):
                goodfiles = fnmatch.filter(files, pattern)
                results.extend(ek(os.path.join, base, f) for f in goodfiles)
            return results

        if not file_path:
            return []

        # don't confuse glob with chars we didn't mean to use
        globbable_file_path = ek(helpers.fixGlob, file_path)

        file_path_list = []

        extensions_to_delete = []

        if subfolders:
            base_name = ek(os.path.basename, globbable_file_path).rpartition('.')[0]
        else:
            base_name = globbable_file_path.rpartition('.')[0]

        if not base_name_only:
            base_name += '.'

        # don't strip it all and use cwd by accident
        if not base_name:
            return []

        # subfolders are only checked in show folder, so names will always be exactly alike
        if subfolders:
            # just create the list of all files starting with the basename
            filelist = recursive_glob(ek(os.path.dirname, globbable_file_path), base_name + '*')
        # this is called when PP, so we need to do the filename check case-insensitive
        else:
            filelist = []

            # get a list of all the files in the folder
            checklist = glob.glob(ek(os.path.join, ek(os.path.dirname, globbable_file_path), '*'))
            # loop through all the files in the folder, and check if they are the same name even when the cases don't match
            for filefound in checklist:

                file_name = filefound.rpartition('.')[0]
                file_extension = filefound.rpartition('.')[2]
                is_subtitle = None

                if file_extension in subtitle_extensions:
                    is_subtitle = True

                if not base_name_only:
                    new_file_name = file_name + '.'
                    sub_file_name = file_name.rpartition('.')[0] + '.'
                else:
                    new_file_name = file_name
                    sub_file_name = file_name.rpartition('.')[0]

                if is_subtitle and sub_file_name.lower() == base_name.lower().replace('[[]', '[').replace('[]]', ']'):
                    language_extensions = tuple('.' + c for c in language_converters['opensubtitles'].codes)
                    if file_name.lower().endswith(language_extensions) and (len(filefound.rsplit('.', 2)[1]) in [2, 3]):
                        filelist.append(filefound)
                    elif file_name.lower().endswith('pt-br') and len(filefound.rsplit('.', 2)[1]) == 5:
                        filelist.append(filefound)
                # if there's no difference in the filename add it to the filelist
                elif new_file_name.lower() == base_name.lower().replace('[[]', '[').replace('[]]', ']'):
                    filelist.append(filefound)

        for associated_file_path in filelist:
            # Exclude the video file we are post-processing
            if associated_file_path == file_path:
                continue

            # Exlude non-subtitle files with the 'only subtitles' option (not implemented yet)
            # if subtitles_only and not associated_file_path[-3:] in subtitle_extensions:
            #     continue

            # Exclude .rar files from associated list
            if re.search(r'(^.+\.(rar|r\d+)$)', associated_file_path):
                continue

            # Add the extensions that the user doesn't allow to the 'extensions_to_delete' list
            if sickbeard.MOVE_ASSOCIATED_FILES:
                allowed_extensions = sickbeard.ALLOWED_EXTENSIONS.split(",")
                if not associated_file_path.rpartition('.')[2] in allowed_extensions:
                    if ek(os.path.isfile, associated_file_path):
                        extensions_to_delete.append(associated_file_path)

            if ek(os.path.isfile, associated_file_path):
                file_path_list.append(associated_file_path)

        if file_path_list:
            self._log(u"Found the following associated files for %s: %s" % (file_path, file_path_list), logger.DEBUG)
            if extensions_to_delete:
                # Rebuild the 'file_path_list' list only with the extensions the user allows
                file_path_list = [associated_file for associated_file in file_path_list if associated_file not in extensions_to_delete]
                self._delete(extensions_to_delete)
        else:
            self._log(u"No associated files for %s were found during this pass" % file_path, logger.DEBUG)

        return file_path_list