    def process(self):
        if self.args.d:
            # drop the list
            self.dropCollection()
        elif self.args.i:
            # get import file
            textfile=self.args.i
            # check if the collection is empty
            count=self.countItems()
            if count>0 and self.args.f is False:
                # not empty and not forced to drop
                print("list already populated")
            else:
                # drop collection and repopulate it
                self.dropCollection()
                self.importList(textfile)
        elif self.args.e:
            # get export file
            textfile=self.args.e
            self.exportList(textfile)
        elif self.args.a or self.args.A:
            # get list of cpe's to add
            if self.args.a:
                cpeList = self.args.a
            else:
                cpeList = [x for x in open(self.args.A[0])]
            # add each item from the list
            count=0
            for cpeID in cpeList:
                if self.insert(cpeID):
                    count+=1
            if self.args.v:
                print("{:d} products added to the list".format(count))
        elif self.args.r or self.args.R:
            # get list of cpe's to remove
            if self.args.r:
                cpeList = self.args.r
            else:
                cpeList = [x for x in open(self.args.R[0])]
            # remove each item from the list
            count=0
            for cpeID in cpeList:
                amount=self.remove(cpeID)
                count+=amount
            if self.args.v:
                print("{:d} products removed from the list".format(count))