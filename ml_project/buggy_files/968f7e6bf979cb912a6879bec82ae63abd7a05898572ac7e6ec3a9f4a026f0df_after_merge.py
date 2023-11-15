                def reset_stat(tarinfo):
                    if tarinfo.type != tarfile.SYMTYPE:
                        existing_is_exec = tarinfo.mode & stat.S_IXUSR
                        tarinfo.mode = 0o0755 if existing_is_exec or tarinfo.isdir() else 0o0644
                    tarinfo.uid = tarinfo.gid = 0
                    tarinfo.uname = tarinfo.gname = ''

                    return tarinfo