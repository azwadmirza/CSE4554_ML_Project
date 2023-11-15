def update():
    '''
    Update caches of the storage containers.

    Compares the md5 of the files on disk to the md5 of the blobs in the
    container, and only updates if necessary.

    Also processes deletions by walking the container caches and comparing
    with the list of blobs in the container
    '''
    for container in __opts__['azurefs']:
        path = _get_container_path(container)
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            elif not os.path.isdir(path):
                shutil.rmtree(path)
                os.makedirs(path)
        except Exception as exc:
            log.exception('Error occurred creating cache directory for azurefs')
            continue
        blob_service = _get_container_service(container)
        name = container['container_name']
        try:
            blob_list = blob_service.list_blobs(name)
        except Exception as exc:
            log.exception('Error occurred fetching blob list for azurefs')
            continue

        # Walk the cache directory searching for deletions
        blob_names = [blob.name for blob in blob_list]
        blob_set = set(blob_names)
        for root, dirs, files in os.walk(path):
            for f in files:
                fname = os.path.join(root, f)
                relpath = os.path.relpath(fname, path)
                if relpath not in blob_set:
                    salt.fileserver.wait_lock(fname + '.lk', fname)
                    try:
                        os.unlink(fname)
                    except Exception:
                        pass
            if not dirs and not files:
                shutil.rmtree(root)

        for blob in blob_list:
            fname = os.path.join(path, blob.name)
            update = False
            if os.path.exists(fname):
                # File exists, check the hashes
                source_md5 = blob.properties.content_settings.content_md5
                local_md5 = base64.b64encode(salt.utils.get_hash(fname, 'md5').decode('hex'))
                if local_md5 != source_md5:
                    update = True
            else:
                update = True

            if update:
                if not os.path.exists(os.path.dirname(fname)):
                    os.makedirs(os.path.dirname(fname))
                # Lock writes
                lk_fn = fname + '.lk'
                salt.fileserver.wait_lock(lk_fn, fname)
                with salt.utils.fopen(lk_fn, 'w+') as fp_:
                    fp_.write('')

                try:
                    blob_service.get_blob_to_path(name, blob.name, fname)
                except Exception as exc:
                    log.exception('Error occurred fetching blob from azurefs')
                    continue

                # Unlock writes
                try:
                    os.unlink(lk_fn)
                except Exception:
                    pass

        # Write out file list
        container_list = path + '.list'
        lk_fn = container_list + '.lk'
        salt.fileserver.wait_lock(lk_fn, container_list)
        with salt.utils.fopen(lk_fn, 'w+') as fp_:
            fp_.write('')
        with salt.utils.fopen(container_list, 'w') as fp_:
            fp_.write(json.dumps(blob_names))
        try:
            os.unlink(lk_fn)
        except Exception:
            pass
        try:
            hash_cachedir = os.path.join(__opts__['cachedir'], 'azurefs', 'hashes')
            if os.path.exists(hash_cachedir):
                shutil.rmtree(hash_cachedir)
        except Exception:
            log.exception('Problem occurred trying to invalidate hash cach for azurefs')