    def is_unarchived(self):
        # BSD unzip doesn't support zipinfo listings with timestamp.
        cmd = [self.zipinfocmd_path, '-T', '-s', self.src]
        if self.excludes:
            cmd.extend(['-x', ] + self.excludes)
        rc, out, err = self.module.run_command(cmd)

        old_out = out
        diff = ''
        out = ''
        if rc == 0:
            unarchived = True
        else:
            unarchived = False

        # Get some information related to user/group ownership
        umask = os.umask(0)
        os.umask(umask)
        systemtype = platform.system()

        # Get current user and group information
        groups = os.getgroups()
        run_uid = os.getuid()
        run_gid = os.getgid()
        try:
            run_owner = pwd.getpwuid(run_uid).pw_name
        except (TypeError, KeyError):
            run_owner = run_uid
        try:
            run_group = grp.getgrgid(run_gid).gr_name
        except (KeyError, ValueError, OverflowError):
            run_group = run_gid

        # Get future user ownership
        fut_owner = fut_uid = None
        if self.file_args['owner']:
            try:
                tpw = pwd.getpwnam(self.file_args['owner'])
            except KeyError:
                try:
                    tpw = pwd.getpwuid(self.file_args['owner'])
                except (TypeError, KeyError):
                    tpw = pwd.getpwuid(run_uid)
            fut_owner = tpw.pw_name
            fut_uid = tpw.pw_uid
        else:
            try:
                fut_owner = run_owner
            except Exception:
                pass
            fut_uid = run_uid

        # Get future group ownership
        fut_group = fut_gid = None
        if self.file_args['group']:
            try:
                tgr = grp.getgrnam(self.file_args['group'])
            except (ValueError, KeyError):
                try:
                    tgr = grp.getgrgid(self.file_args['group'])
                except (KeyError, ValueError, OverflowError):
                    tgr = grp.getgrgid(run_gid)
            fut_group = tgr.gr_name
            fut_gid = tgr.gr_gid
        else:
            try:
                fut_group = run_group
            except Exception:
                pass
            fut_gid = run_gid

        for line in old_out.splitlines():
            change = False

            pcs = line.split(None, 7)
            if len(pcs) != 8:
                # Too few fields... probably a piece of the header or footer
                continue

            # Check first and seventh field in order to skip header/footer
            if len(pcs[0]) != 7 and len(pcs[0]) != 10:
                continue
            if len(pcs[6]) != 15:
                continue

            # Possible entries:
            #   -rw-rws---  1.9 unx    2802 t- defX 11-Aug-91 13:48 perms.2660
            #   -rw-a--     1.0 hpf    5358 Tl i4:3  4-Dec-91 11:33 longfilename.hpfs
            #   -r--ahs     1.1 fat    4096 b- i4:2 14-Jul-91 12:58 EA DATA. SF
            #   --w-------  1.0 mac   17357 bx i8:2  4-May-92 04:02 unzip.macr
            if pcs[0][0] not in 'dl-?' or not frozenset(pcs[0][1:]).issubset('rwxstah-'):
                continue

            ztype = pcs[0][0]
            permstr = pcs[0][1:]
            version = pcs[1]
            ostype = pcs[2]
            size = int(pcs[3])
            path = to_text(pcs[7], errors='surrogate_or_strict')

            # Skip excluded files
            if path in self.excludes:
                out += 'Path %s is excluded on request\n' % path
                continue

            # Itemized change requires L for symlink
            if path[-1] == '/':
                if ztype != 'd':
                    err += 'Path %s incorrectly tagged as "%s", but is a directory.\n' % (path, ztype)
                ftype = 'd'
            elif ztype == 'l':
                ftype = 'L'
            elif ztype == '-':
                ftype = 'f'
            elif ztype == '?':
                ftype = 'f'

            # Some files may be storing FAT permissions, not Unix permissions
            # For FAT permissions, we will use a base permissions set of 777 if the item is a directory or has the execute bit set.  Otherwise, 666.
            #     This permission will then be modified by the system UMask.
            # BSD always applies the Umask, even to Unix permissions.
            # For Unix style permissions on Linux or Mac, we want to use them directly.
            #     So we set the UMask for this file to zero.  That permission set will then be unchanged when calling _permstr_to_octal

            if len(permstr) == 6:
                if path[-1] == '/':
                    permstr = 'rwxrwxrwx'
                elif permstr == 'rwx---':
                    permstr = 'rwxrwxrwx'
                else:
                    permstr = 'rw-rw-rw-'
                file_umask = umask
            elif 'bsd' in systemtype.lower():
                file_umask = umask
            else:
                file_umask = 0

            # Test string conformity
            if len(permstr) != 9 or not ZIP_FILE_MODE_RE.match(permstr):
                raise UnarchiveError('ZIP info perm format incorrect, %s' % permstr)

            # DEBUG
#            err += "%s%s %10d %s\n" % (ztype, permstr, size, path)

            dest = os.path.join(self.dest, path)
            try:
                st = os.lstat(dest)
            except Exception:
                change = True
                self.includes.append(path)
                err += 'Path %s is missing\n' % path
                diff += '>%s++++++.?? %s\n' % (ftype, path)
                continue

            # Compare file types
            if ftype == 'd' and not stat.S_ISDIR(st.st_mode):
                change = True
                self.includes.append(path)
                err += 'File %s already exists, but not as a directory\n' % path
                diff += 'c%s++++++.?? %s\n' % (ftype, path)
                continue

            if ftype == 'f' and not stat.S_ISREG(st.st_mode):
                change = True
                unarchived = False
                self.includes.append(path)
                err += 'Directory %s already exists, but not as a regular file\n' % path
                diff += 'c%s++++++.?? %s\n' % (ftype, path)
                continue

            if ftype == 'L' and not stat.S_ISLNK(st.st_mode):
                change = True
                self.includes.append(path)
                err += 'Directory %s already exists, but not as a symlink\n' % path
                diff += 'c%s++++++.?? %s\n' % (ftype, path)
                continue

            itemized = list('.%s.......??' % ftype)

            # Note: this timestamp calculation has a rounding error
            # somewhere... unzip and this timestamp can be one second off
            # When that happens, we report a change and re-unzip the file
            dt_object = datetime.datetime(*(time.strptime(pcs[6], '%Y%m%d.%H%M%S')[0:6]))
            timestamp = time.mktime(dt_object.timetuple())

            # Compare file timestamps
            if stat.S_ISREG(st.st_mode):
                if self.module.params['keep_newer']:
                    if timestamp > st.st_mtime:
                        change = True
                        self.includes.append(path)
                        err += 'File %s is older, replacing file\n' % path
                        itemized[4] = 't'
                    elif stat.S_ISREG(st.st_mode) and timestamp < st.st_mtime:
                        # Add to excluded files, ignore other changes
                        out += 'File %s is newer, excluding file\n' % path
                        self.excludes.append(path)
                        continue
                else:
                    if timestamp != st.st_mtime:
                        change = True
                        self.includes.append(path)
                        err += 'File %s differs in mtime (%f vs %f)\n' % (path, timestamp, st.st_mtime)
                        itemized[4] = 't'

            # Compare file sizes
            if stat.S_ISREG(st.st_mode) and size != st.st_size:
                change = True
                err += 'File %s differs in size (%d vs %d)\n' % (path, size, st.st_size)
                itemized[3] = 's'

            # Compare file checksums
            if stat.S_ISREG(st.st_mode):
                crc = crc32(dest)
                if crc != self._crc32(path):
                    change = True
                    err += 'File %s differs in CRC32 checksum (0x%08x vs 0x%08x)\n' % (path, self._crc32(path), crc)
                    itemized[2] = 'c'

            # Compare file permissions

            # Do not handle permissions of symlinks
            if ftype != 'L':

                # Use the new mode provided with the action, if there is one
                if self.file_args['mode']:
                    if isinstance(self.file_args['mode'], int):
                        mode = self.file_args['mode']
                    else:
                        try:
                            mode = int(self.file_args['mode'], 8)
                        except Exception as e:
                            try:
                                mode = AnsibleModule._symbolic_mode_to_octal(st, self.file_args['mode'])
                            except ValueError as e:
                                self.module.fail_json(path=path, msg="%s" % to_native(e), exception=traceback.format_exc())
                # Only special files require no umask-handling
                elif ztype == '?':
                    mode = self._permstr_to_octal(permstr, 0)
                else:
                    mode = self._permstr_to_octal(permstr, file_umask)

                if mode != stat.S_IMODE(st.st_mode):
                    change = True
                    itemized[5] = 'p'
                    err += 'Path %s differs in permissions (%o vs %o)\n' % (path, mode, stat.S_IMODE(st.st_mode))

            # Compare file user ownership
            owner = uid = None
            try:
                owner = pwd.getpwuid(st.st_uid).pw_name
            except (TypeError, KeyError):
                uid = st.st_uid

            # If we are not root and requested owner is not our user, fail
            if run_uid != 0 and (fut_owner != run_owner or fut_uid != run_uid):
                raise UnarchiveError('Cannot change ownership of %s to %s, as user %s' % (path, fut_owner, run_owner))

            if owner and owner != fut_owner:
                change = True
                err += 'Path %s is owned by user %s, not by user %s as expected\n' % (path, owner, fut_owner)
                itemized[6] = 'o'
            elif uid and uid != fut_uid:
                change = True
                err += 'Path %s is owned by uid %s, not by uid %s as expected\n' % (path, uid, fut_uid)
                itemized[6] = 'o'

            # Compare file group ownership
            group = gid = None
            try:
                group = grp.getgrgid(st.st_gid).gr_name
            except (KeyError, ValueError, OverflowError):
                gid = st.st_gid

            if run_uid != 0 and fut_gid not in groups:
                raise UnarchiveError('Cannot change group ownership of %s to %s, as user %s' % (path, fut_group, run_owner))

            if group and group != fut_group:
                change = True
                err += 'Path %s is owned by group %s, not by group %s as expected\n' % (path, group, fut_group)
                itemized[6] = 'g'
            elif gid and gid != fut_gid:
                change = True
                err += 'Path %s is owned by gid %s, not by gid %s as expected\n' % (path, gid, fut_gid)
                itemized[6] = 'g'

            # Register changed files and finalize diff output
            if change:
                if path not in self.includes:
                    self.includes.append(path)
                diff += '%s %s\n' % (''.join(itemized), path)

        if self.includes:
            unarchived = False

        # DEBUG
#        out = old_out + out

        return dict(unarchived=unarchived, rc=rc, out=out, err=err, cmd=cmd, diff=diff)