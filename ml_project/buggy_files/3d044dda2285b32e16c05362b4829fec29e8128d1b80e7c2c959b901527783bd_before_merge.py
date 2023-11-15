def Verify(mirror_rp, inc_rp, verify_time):
    """Compute SHA1 sums of repository files and check against metadata"""
    assert mirror_rp.conn is Globals.local_connection
    repo_iter = RepoSide.init_and_get_iter(mirror_rp, inc_rp, verify_time)
    base_index = RepoSide.mirror_base.index

    bad_files = 0
    for repo_rorp in repo_iter:
        if not repo_rorp.isreg():
            continue
        if not repo_rorp.has_sha1():
            log.Log(
                "Warning: Cannot find SHA1 digest for file %s,\n"
                "perhaps because this feature was added in v1.1.1" %
                (repo_rorp.get_safeindexpath(), ), 2)
            continue
        fp = RepoSide.rf_cache.get_fp(base_index + repo_rorp.index, repo_rorp)
        computed_hash = hash.compute_sha1_fp(fp)
        if computed_hash == repo_rorp.get_sha1():
            log.Log(
                "Verified SHA1 digest of %s" % repo_rorp.get_safeindexpath(),
                5)
        else:
            bad_files += 1
            log.Log(
                "Warning: Computed SHA1 digest of %s\n   %s\n"
                "doesn't match recorded digest of\n   %s\n"
                "Your backup repository may be corrupted!" %
                (repo_rorp.get_safeindexpath(), computed_hash,
                 repo_rorp.get_sha1()), 2)
    RepoSide.close_rf_cache()
    if not bad_files:
        log.Log("Every file verified successfully.", 3)
    return bad_files