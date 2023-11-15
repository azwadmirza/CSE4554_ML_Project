def _run_delly(bam_files, chrom, ref_file, work_dir, items):
    """Run delly, calling structural variations for the specified type.
    """
    batch = sshared.get_cur_batch(items)
    ext = "-%s-svs" % batch if batch else "-svs"
    out_file = os.path.join(work_dir, "%s%s-%s.bcf"
                            % (os.path.splitext(os.path.basename(bam_files[0]))[0], ext, chrom))
    final_file = "%s.vcf.gz" % (utils.splitext_plus(out_file)[0])
    cores = min(utils.get_in(items[0], ("config", "algorithm", "num_cores"), 1),
                len(bam_files))
    if not utils.file_exists(out_file) and not utils.file_exists(final_file):
        with file_transaction(items[0], out_file) as tx_out_file:
            if sshared.has_variant_regions(items, out_file, chrom):
                exclude = ["-x", _delly_exclude_file(items, out_file, chrom)]
                cmd = ["delly", "call", "-g", ref_file, "-o", tx_out_file] + exclude + bam_files
                multi_cmd = "export OMP_NUM_THREADS=%s && export LC_ALL=C && " % cores
                try:
                    do.run(multi_cmd + " ".join(cmd), "delly structural variant")
                except subprocess.CalledProcessError as msg:
                    # Small input samples, write an empty vcf
                    if "Sample has not enough data to estimate library parameters" in str(msg):
                        pass
                    # delly returns an error exit code if there are no variants
                    elif "No structural variants found" not in str(msg):
                        raise
    return [_bgzip_and_clean(out_file, items)]