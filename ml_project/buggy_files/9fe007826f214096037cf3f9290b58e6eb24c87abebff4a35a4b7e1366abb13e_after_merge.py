    def addToIndex(self, wordindex, fileindex, words, dir, fileinfo):
        index = len(fileindex)
        for i in words:
            if i not in wordindex:
                wordindex[i] = [index]
            else:
                wordindex[i] = wordindex[i] + [index]
        fileindex.append((os.path.join(dir, fileinfo[0]),) + fileinfo[1:])