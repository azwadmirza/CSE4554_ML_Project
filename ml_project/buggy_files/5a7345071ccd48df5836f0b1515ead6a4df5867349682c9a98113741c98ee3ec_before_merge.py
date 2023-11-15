    def install_targets(self, d):
        for t in d.targets:
            fname = check_for_stampfile(t.fname)
            outdir = get_destdir_path(d, t.outdir)
            outname = os.path.join(outdir, os.path.basename(fname))
            final_path = os.path.join(d.prefix, t.outdir, os.path.basename(fname))
            aliases = t.aliases
            should_strip = t.strip
            install_rpath = t.install_rpath
            install_name_mappings = t.install_name_mappings
            install_mode = t.install_mode
            d.dirmaker.makedirs(outdir, exist_ok=True)
            if not os.path.exists(fname):
                raise RuntimeError('File {!r} could not be found'.format(fname))
            elif os.path.isfile(fname):
                self.do_copyfile(fname, outname)
                set_mode(outname, install_mode, d.install_umask)
                if should_strip and d.strip_bin is not None:
                    if fname.endswith('.jar'):
                        print('Not stripping jar target:', os.path.basename(fname))
                        continue
                    print('Stripping target {!r}'.format(fname))
                    ps, stdo, stde = Popen_safe(d.strip_bin + [outname])
                    if ps.returncode != 0:
                        print('Could not strip file.\n')
                        print('Stdout:\n%s\n' % stdo)
                        print('Stderr:\n%s\n' % stde)
                        sys.exit(1)
                pdb_filename = os.path.splitext(fname)[0] + '.pdb'
                if not should_strip and os.path.exists(pdb_filename):
                    pdb_outname = os.path.splitext(outname)[0] + '.pdb'
                    self.do_copyfile(pdb_filename, pdb_outname)
                    set_mode(pdb_outname, install_mode, d.install_umask)
            elif os.path.isdir(fname):
                fname = os.path.join(d.build_dir, fname.rstrip('/'))
                outname = os.path.join(outdir, os.path.basename(fname))
                self.do_copydir(d, fname, outname, None, install_mode)
            else:
                raise RuntimeError('Unknown file type for {!r}'.format(fname))
            printed_symlink_error = False
            for alias, to in aliases.items():
                try:
                    symlinkfilename = os.path.join(outdir, alias)
                    try:
                        os.unlink(symlinkfilename)
                    except FileNotFoundError:
                        pass
                    os.symlink(to, symlinkfilename)
                    append_to_log(self.lf, symlinkfilename)
                except (NotImplementedError, OSError):
                    if not printed_symlink_error:
                        print("Symlink creation does not work on this platform. "
                              "Skipping all symlinking.")
                        printed_symlink_error = True
            if os.path.isfile(outname):
                try:
                    depfixer.fix_rpath(outname, install_rpath, final_path,
                                       install_name_mappings, verbose=False)
                except SystemExit as e:
                    if isinstance(e.code, int) and e.code == 0:
                        pass
                    else:
                        raise