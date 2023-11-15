    def atomic_move(self, src, dest, unsafe_writes=False):
        '''atomically move src to dest, copying attributes from dest, returns true on success
        it uses os.rename to ensure this as it is an atomic operation, rest of the function is
        to work around limitations, corner cases and ensure selinux context is saved if possible'''
        context = None
        dest_stat = None
        b_src = to_bytes(src, errors='surrogate_or_strict')
        b_dest = to_bytes(dest, errors='surrogate_or_strict')
        if os.path.exists(b_dest):
            try:
                dest_stat = os.stat(b_dest)
                os.chmod(b_src, dest_stat.st_mode & PERM_BITS)
                os.chown(b_src, dest_stat.st_uid, dest_stat.st_gid)
            except OSError:
                e = get_exception()
                if e.errno != errno.EPERM:
                    raise
            if self.selinux_enabled():
                context = self.selinux_context(dest)
        else:
            if self.selinux_enabled():
                context = self.selinux_default_context(dest)

        creating = not os.path.exists(b_dest)

        try:
            login_name = os.getlogin()
        except OSError:
            # not having a tty can cause the above to fail, so
            # just get the LOGNAME environment variable instead
            login_name = os.environ.get('LOGNAME', None)

        # if the original login_name doesn't match the currently
        # logged-in user, or if the SUDO_USER environment variable
        # is set, then this user has switched their credentials
        switched_user = login_name and login_name != pwd.getpwuid(os.getuid())[0] or os.environ.get('SUDO_USER')

        try:
            # Optimistically try a rename, solves some corner cases and can avoid useless work, throws exception if not atomic.
            os.rename(b_src, b_dest)
        except (IOError, OSError):
            e = get_exception()
            if e.errno not in [errno.EPERM, errno.EXDEV, errno.EACCES, errno.ETXTBSY, errno.EBUSY]:
                # only try workarounds for errno 18 (cross device), 1 (not permitted),  13 (permission denied)
                # and 26 (text file busy) which happens on vagrant synced folders and other 'exotic' non posix file systems
                self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))
            else:
                b_dest_dir = os.path.dirname(b_dest)
                # Use bytes here.  In the shippable CI, this fails with
                # a UnicodeError with surrogateescape'd strings for an unknown
                # reason (doesn't happen in a local Ubuntu16.04 VM)
                native_dest_dir = b_dest_dir
                native_suffix = os.path.basename(b_dest)
                native_prefix = b('.ansible_tmp')
                try:
                    tmp_dest_fd, tmp_dest_name = tempfile.mkstemp(
                        prefix=native_prefix, dir=native_dest_dir, suffix=native_suffix)
                except (OSError, IOError):
                    e = get_exception()
                    self.fail_json(msg='The destination directory (%s) is not writable by the current user. Error was: %s' % (os.path.dirname(dest), e))
                except TypeError:
                    # We expect that this is happening because python3.4.x and
                    # below can't handle byte strings in mkstemp().  Traceback
                    # would end in something like:
                    #     file = _os.path.join(dir, pre + name + suf)
                    # TypeError: can't concat bytes to str
                    self.fail_json(msg='Failed creating temp file for atomic move.  This usually happens when using Python3 less than Python3.5.  Please use Python2.x or Python3.5 or greater.', exception=sys.exc_info())

                b_tmp_dest_name = to_bytes(tmp_dest_name, errors='surrogate_or_strict')

                try:
                    try:
                        # close tmp file handle before file operations to prevent text file busy errors on vboxfs synced folders (windows host)
                        os.close(tmp_dest_fd)
                        # leaves tmp file behind when sudo and not root
                        if switched_user and os.getuid() != 0:
                            # cleanup will happen by 'rm' of tempdir
                            # copy2 will preserve some metadata
                            shutil.copy2(b_src, b_tmp_dest_name)
                        else:
                            shutil.move(b_src, b_tmp_dest_name)
                        if self.selinux_enabled():
                            self.set_context_if_different(
                                b_tmp_dest_name, context, False)
                        try:
                            tmp_stat = os.stat(b_tmp_dest_name)
                            if dest_stat and (tmp_stat.st_uid != dest_stat.st_uid or tmp_stat.st_gid != dest_stat.st_gid):
                                os.chown(b_tmp_dest_name, dest_stat.st_uid, dest_stat.st_gid)
                        except OSError:
                            e = get_exception()
                            if e.errno != errno.EPERM:
                                raise
                        try:
                            os.rename(b_tmp_dest_name, b_dest)
                        except (shutil.Error, OSError, IOError):
                            e = get_exception()
                            if unsafe_writes:
                                self._unsafe_writes(b_tmp_dest_name, b_dest, e)
                            else:
                                self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))
                    except (shutil.Error, OSError, IOError):
                        e = get_exception()
                        self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))
                finally:
                    self.cleanup(b_tmp_dest_name)

        if creating:
            # make sure the file has the correct permissions
            # based on the current value of umask
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(b_dest, DEFAULT_PERM & ~umask)
            if switched_user:
                os.chown(b_dest, os.getuid(), os.getgid())

        if self.selinux_enabled():
            # rename might not preserve context
            self.set_context_if_different(dest, context, False)