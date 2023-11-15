    def _save(self, obj, path):
        if not self._atomic:
            torch.save(obj, path)

        else:
            tmp = tempfile.NamedTemporaryFile(delete=False, dir=self._dirname)

            try:
                torch.save(obj, tmp.file)

            except BaseException:
                tmp.close()
                os.remove(tmp.name)
                raise

            else:
                tmp.close()
                os.rename(tmp.name, path)