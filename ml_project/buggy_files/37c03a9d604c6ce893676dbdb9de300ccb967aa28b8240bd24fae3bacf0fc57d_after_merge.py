    def _force_local(cls, pex_file, pex_info):
        if pex_info.code_hash is None:
            # Do not support force_local if code_hash is not set. (It should always be set.)
            return pex_file
        explode_dir = os.path.join(pex_info.zip_unsafe_cache, pex_info.code_hash)
        TRACER.log("PEX is not zip safe, exploding to %s" % explode_dir)
        with atomic_directory(explode_dir, exclusive=True) as explode_tmp:
            if explode_tmp:
                with TRACER.timed("Unzipping %s" % pex_file):
                    with open_zip(pex_file) as pex_zip:
                        pex_files = (
                            x
                            for x in pex_zip.namelist()
                            if not x.startswith(pex_builder.BOOTSTRAP_DIR)
                            and not x.startswith(pex_info.internal_cache)
                        )
                        pex_zip.extractall(explode_tmp, pex_files)
        return explode_dir