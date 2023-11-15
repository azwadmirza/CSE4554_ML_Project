    def writeDownloadQueue(self):
        self.config_lock.acquire()
        realfile = os.path.join(self.data_dir, 'transfers.pickle')
        tmpfile = realfile + '.tmp'
        backupfile = realfile + ' .backup'
        try:
            handle = open(tmpfile, 'wb')
        except Exception as inst:
            log.addwarning(_("Something went wrong while opening your transfer list: %(error)s") % {'error': str(inst)})
        else:
            try:
                pickle.dump(self.sections['transfers']['downloads'], handle, protocol=pickle.HIGHEST_PROTOCOL)
                handle.close()
                try:
                    # Please let it be atomic...
                    os.rename(tmpfile, realfile)
                except Exception as inst:  # noqa: F841
                    # ...ugh. Okay, how about...
                    try:
                        os.unlink(backupfile)
                    except Exception:
                        pass
                    os.rename(realfile, backupfile)
                    os.rename(tmpfile, realfile)
            except Exception as inst:
                log.addwarning(_("Something went wrong while writing your transfer list: %(error)s") % {'error': str(inst)})
        finally:
            try:
                handle.close()
            except Exception:
                pass
        self.config_lock.release()