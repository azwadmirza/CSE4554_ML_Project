def create_paramfile(trans, uploaded_datasets):
    """
    Create the upload tool's JSON "param" file.
    """
    def _chown(path):
        try:
            # get username from email/username
            pwent = trans.user.system_user_pwent(trans.app.config.real_system_username)
            cmd = shlex.split(trans.app.config.external_chown_script)
            cmd.extend([path, pwent[0], str(pwent[3])])
            log.debug('Changing ownership of %s with: %s' % (path, ' '.join(cmd)))
            p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            assert p.returncode == 0, stderr
        except Exception as e:
            log.warning('Changing ownership of uploaded file %s failed: %s' % (path, str(e)))

    # TODO: json_file should go in the working directory
    json_file = tempfile.mkstemp()
    json_file_path = json_file[1]
    json_file = os.fdopen(json_file[0], 'w')
    for uploaded_dataset in uploaded_datasets:
        data = uploaded_dataset.data
        if uploaded_dataset.type == 'composite':
            # we need to init metadata before the job is dispatched
            data.init_meta()
            for meta_name, meta_value in uploaded_dataset.metadata.items():
                setattr(data.metadata, meta_name, meta_value)
            trans.sa_session.add(data)
            trans.sa_session.flush()
            json = dict(file_type=uploaded_dataset.file_type,
                        dataset_id=data.dataset.id,
                        dbkey=uploaded_dataset.dbkey,
                        type=uploaded_dataset.type,
                        metadata=uploaded_dataset.metadata,
                        primary_file=uploaded_dataset.primary_file,
                        composite_file_paths=uploaded_dataset.composite_files,
                        composite_files=dict((k, v.__dict__) for k, v in data.datatype.get_composite_files(data).items()))
        else:
            try:
                is_binary = uploaded_dataset.datatype.is_binary
            except Exception:
                is_binary = None
            try:
                link_data_only = uploaded_dataset.link_data_only
            except Exception:
                link_data_only = 'copy_files'
            try:
                uuid_str = uploaded_dataset.uuid
            except Exception:
                uuid_str = None
            try:
                purge_source = uploaded_dataset.purge_source
            except Exception:
                purge_source = True
            try:
                user_ftp_dir = os.path.abspath(trans.user_ftp_dir)
            except Exception:
                user_ftp_dir = None
            if user_ftp_dir and uploaded_dataset.path.startswith(user_ftp_dir):
                uploaded_dataset.type = 'ftp_import'
            json = dict(file_type=uploaded_dataset.file_type,
                        ext=uploaded_dataset.ext,
                        name=uploaded_dataset.name,
                        dataset_id=data.dataset.id,
                        dbkey=uploaded_dataset.dbkey,
                        type=uploaded_dataset.type,
                        is_binary=is_binary,
                        link_data_only=link_data_only,
                        uuid=uuid_str,
                        to_posix_lines=getattr(uploaded_dataset, "to_posix_lines", True),
                        auto_decompress=getattr(uploaded_dataset, "auto_decompress", True),
                        purge_source=purge_source,
                        space_to_tab=uploaded_dataset.space_to_tab,
                        in_place=trans.app.config.external_chown_script is None,
                        check_content=trans.app.config.check_upload_content,
                        path=uploaded_dataset.path)
            # TODO: This will have to change when we start bundling inputs.
            # Also, in_place above causes the file to be left behind since the
            # user cannot remove it unless the parent directory is writable.
            if link_data_only == 'copy_files' and trans.app.config.external_chown_script:
                _chown(uploaded_dataset.path)
        json_file.write(dumps(json) + '\n')
    json_file.close()
    if trans.app.config.external_chown_script:
        _chown(json_file_path)
    return json_file_path