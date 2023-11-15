    def to_string(self, indent):
        # type: (int) -> unicode
        res = ['\t' * indent]  # type: List[unicode]
        if not self.parent:
            res.append('::')
        else:
            if self.templateParams:
                res.append(text_type(self.templateParams))
                res.append('\n')
                res.append('\t' * indent)
            if self.identOrOp:
                res.append(text_type(self.identOrOp))
            else:
                res.append(text_type(self.declaration))
            if self.templateArgs:
                res.append(text_type(self.templateArgs))
            if self.declaration:
                res.append(": ")
                if self.isRedeclaration:
                    res.append('!!duplicate!! ')
                res.append(text_type(self.declaration))
        if self.docname:
            res.append('\t(')
            res.append(self.docname)
            res.append(')')
        res.append('\n')
        return ''.join(res)