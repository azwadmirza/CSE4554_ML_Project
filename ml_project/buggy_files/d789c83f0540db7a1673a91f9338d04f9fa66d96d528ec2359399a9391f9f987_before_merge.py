    def dump(self,  file=None):
        file = file or sys.stdout
        print(("begin parfor {}".format(self.id)).center(20,'-'), file=file)
        print("index_var = ", self.index_var)
        for loopnest in self.loop_nests:
            print(loopnest, file=file)
        print("init block:", file=file)
        self.init_block.dump()
        for offset, block in sorted(self.loop_body.items()):
            print('label %s:' % (offset,), file=file)
            block.dump(file)
        print(("end parfor").center(20,'-'), file=file)