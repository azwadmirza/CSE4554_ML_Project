    def exe(self):
        for obj in gdb.objfiles():
            if obj.filename:
                return obj.filename
            break
        if self.alive:
            auxv = pwndbg.auxv.get()
            return auxv['AT_EXECFN']