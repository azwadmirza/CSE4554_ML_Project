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