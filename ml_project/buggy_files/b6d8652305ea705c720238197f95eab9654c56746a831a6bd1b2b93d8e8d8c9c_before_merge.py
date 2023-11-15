  def force_local(cls, pex, pex_info):
    if pex_info.code_hash is None:
      # Do not support force_local if code_hash is not set. (It should always be set.)
      return pex
    explode_dir = os.path.join(pex_info.zip_unsafe_cache, pex_info.code_hash)
    TRACER.log('PEX is not zip safe, exploding to %s' % explode_dir)
    if not os.path.exists(explode_dir):
      explode_tmp = explode_dir + '.' + uuid.uuid4().hex
      with TRACER.timed('Unzipping %s' % pex):
        try:
          safe_mkdir(explode_tmp)
          with open_zip(pex) as pex_zip:
            pex_files = (x for x in pex_zip.namelist()
                         if not x.startswith(pex_builder.BOOTSTRAP_DIR) and
                            not x.startswith(PexInfo.INTERNAL_CACHE))
            pex_zip.extractall(explode_tmp, pex_files)
        except:  # noqa: T803
          safe_rmtree(explode_tmp)
          raise
      TRACER.log('Renaming %s to %s' % (explode_tmp, explode_dir))
      rename_if_empty(explode_tmp, explode_dir)
    return explode_dir