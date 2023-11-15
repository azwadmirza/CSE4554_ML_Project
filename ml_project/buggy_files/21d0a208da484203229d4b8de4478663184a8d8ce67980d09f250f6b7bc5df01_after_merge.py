def _package_conf_ordering(conf, clean=True, keep_backup=False):
    '''
    Move entries in the correct file.
    '''
    if conf in SUPPORTED_CONFS:
        rearrange = []
        path = BASE_PATH.format(conf)

        backup_files = []

        for triplet in os.walk(path):
            for file_name in triplet[2]:
                file_path = '{0}/{1}'.format(triplet[0], file_name)
                cp = triplet[0][len(path) + 1:] + '/' + file_name

                shutil.copy(file_path, file_path + '.bak')
                backup_files.append(file_path + '.bak')

                if cp[0] == '/' or len(cp.split('/')) > 2:
                    with salt.utils.files.fopen(file_path) as fp_:
                        rearrange.extend(fp_.readlines())
                    os.remove(file_path)
                else:
                    new_contents = ''
                    with salt.utils.files.fopen(file_path, 'r+') as file_handler:
                        for line in file_handler:
                            try:
                                atom = line.strip().split()[0]
                            except IndexError:
                                new_contents += line
                            else:
                                if atom[0] == '#' or \
                                        portage.dep_getkey(atom) == cp:
                                    new_contents += line
                                else:
                                    rearrange.append(line.strip())
                        if len(new_contents) != 0:
                            file_handler.seek(0)
                            file_handler.truncate(len(new_contents))
                            file_handler.write(new_contents)

                    if len(new_contents) == 0:
                        os.remove(file_path)

        for line in rearrange:
            append_to_package_conf(conf, string=line)

        if not keep_backup:
            for bfile in backup_files:
                try:
                    os.remove(bfile)
                except OSError:
                    pass

        if clean:
            for triplet in os.walk(path):
                if len(triplet[1]) == 0 and len(triplet[2]) == 0 and \
                        triplet[0] != path:
                    shutil.rmtree(triplet[0])