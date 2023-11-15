    def compare_hash(cls, repo_iter):
        """Like above, but also compare sha1 sums of any regular files"""

        def hashes_changed(src_rp, mir_rorp):
            """Return 0 if their data hashes same, 1 otherwise"""
            verify_sha1 = get_hash(mir_rorp)
            if not verify_sha1:
                log.Log(
                    "Warning: Metadata file has no digest for %s, "
                    "unable to compare." % (mir_rorp.get_safeindexpath(), ), 2)
                return 0
            elif (src_rp.getsize() == mir_rorp.getsize()
                  and hash.compute_sha1(src_rp) == verify_sha1):
                return 0
            return 1

        src_iter = cls.get_source_select()
        for src_rp, mir_rorp in rorpiter.Collate2Iters(src_iter, repo_iter):
            report = get_basic_report(src_rp, mir_rorp, hashes_changed)
            if report:
                yield report
            else:
                log_success(src_rp, mir_rorp)