def add_composite_file(dataset, registry, output_path, files_path):
    datatype = None

    # Find data type
    if dataset.file_type is not None:
        try:
            datatype = registry.get_datatype_by_extension(dataset.file_type)
        except Exception:
            print("Unable to instantiate the datatype object for the file type '%s'" % dataset.file_type)

    def to_path(path_or_url):
        is_url = path_or_url.find('://') != -1  # todo fixme
        if is_url:
            try:
                temp_name = sniff.stream_to_file(urlopen(path_or_url), prefix='url_paste')
            except Exception as e:
                raise UploadProblemException('Unable to fetch %s\n%s' % (path_or_url, str(e)))

            return temp_name, is_url

        return path_or_url, is_url

    def make_files_path():
        safe_makedirs(files_path)

    def stage_file(name, composite_file_path, is_binary=False):
        dp = composite_file_path['path']
        path, is_url = to_path(dp)
        if is_url:
            dataset.path = path
            dp = path

        auto_decompress = composite_file_path.get('auto_decompress', True)
        if auto_decompress and not datatype.composite_type and CompressedFile.can_decompress(dp):
            # It isn't an explictly composite datatype, so these are just extra files to attach
            # as composite data. It'd be better if Galaxy was communicating this to the tool
            # a little more explicitly so we didn't need to dispatch on the datatype and so we
            # could attach arbitrary extra composite data to an existing composite datatype if
            # if need be? Perhaps that would be a mistake though.
            CompressedFile(dp).extract(files_path)
        else:
            if not is_binary:
                tmpdir = output_adjacent_tmpdir(output_path)
                tmp_prefix = 'data_id_%s_convert_' % dataset.dataset_id
                if composite_file_path.get('space_to_tab'):
                    sniff.convert_newlines_sep2tabs(dp, tmp_dir=tmpdir, tmp_prefix=tmp_prefix)
                else:
                    sniff.convert_newlines(dp, tmp_dir=tmpdir, tmp_prefix=tmp_prefix)

            file_output_path = os.path.join(files_path, name)
            shutil.move(dp, file_output_path)

            # groom the dataset file content if required by the corresponding datatype definition
            if datatype.dataset_content_needs_grooming(file_output_path):
                datatype.groom_dataset_content(file_output_path)

    # Do we have pre-defined composite files from the datatype definition.
    if dataset.composite_files:
        make_files_path()
        for name, value in dataset.composite_files.items():
            value = bunch.Bunch(**value)
            if value.name not in dataset.composite_file_paths:
                raise UploadProblemException("Failed to find file_path %s in %s" % (value.name, dataset.composite_file_paths))
            if dataset.composite_file_paths[value.name] is None and not value.optional:
                raise UploadProblemException('A required composite data file was not provided (%s)' % name)
            elif dataset.composite_file_paths[value.name] is not None:
                composite_file_path = dataset.composite_file_paths[value.name]
                stage_file(name, composite_file_path, value.is_binary)

    # Do we have ad-hoc user supplied composite files.
    elif dataset.composite_file_paths:
        make_files_path()
        for key, composite_file in dataset.composite_file_paths.items():
            stage_file(key, composite_file)  # TODO: replace these defaults

    # Move the dataset to its "real" path
    primary_file_path, _ = to_path(dataset.primary_file)
    shutil.move(primary_file_path, output_path)

    # Write the job info
    return dict(type='dataset',
                dataset_id=dataset.dataset_id,
                stdout='uploaded %s file' % dataset.file_type)