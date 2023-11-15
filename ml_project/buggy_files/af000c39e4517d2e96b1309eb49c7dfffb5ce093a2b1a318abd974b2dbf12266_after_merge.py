    def write(self, root, sentinels=True):
        """Write a 4.x derived file.
        root is the position of an @<file> node.
        sentinels will be False for @clean and @nosent nodes.
        """
        at, c = self, self.c
        try:
            c.endEditing()
            fileName = at.initWriteIvars(root, root.anyAtFileNodeName(), sentinels=sentinels)
            if not fileName or not at.precheck(fileName, root):
                if sentinels:
                    # Raise dialog warning of data loss.
                    at.addToOrphanList(root)
                else:
                    # #1450: No danger of data loss.
                    pass
                return
            at.openOutputStream()
            at.putFile(root, sentinels=sentinels)
            at.warnAboutOrphandAndIgnoredNodes()
            contents = at.closeOutputStream()
            if at.errors:
                g.es("not written:", g.shortFileName(fileName))
                at.addToOrphanList(root)
            else:
                at.replaceFile(contents, at.encoding, fileName, root)
        except Exception:
            if hasattr(self.root.v, 'tnodeList'):
                delattr(self.root.v, 'tnodeList')
            at.writeException(fileName, root)