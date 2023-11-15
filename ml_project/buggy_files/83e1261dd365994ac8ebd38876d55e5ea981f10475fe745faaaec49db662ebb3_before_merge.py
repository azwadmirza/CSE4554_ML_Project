    def importList(self, importFile):
        count=0
        # read each line from the import file and regex them to a cpe format
        try:
            for line in open(importFile):
                if self.insert(line):
                    count+=1
            if self.args.v:
                print("{:d} products added to the list".format(count))
        except IOError:
            print('Could not open the file')
            sys.exit()