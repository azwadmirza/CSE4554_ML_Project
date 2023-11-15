    def __init__(self,
                 parent,          # type: Symbol
                 identOrOp,       # type: Union[ASTIdentifier, ASTOperator]
                 templateParams,  # type: Any
                 templateArgs,    # type: Any
                 declaration,     # type: ASTDeclaration
                 docname          # type: unicode
                 ):
        # type: (...) -> None
        self.parent = parent
        self.identOrOp = identOrOp
        self.templateParams = templateParams  # template<templateParams>
        self.templateArgs = templateArgs  # identifier<templateArgs>
        self.declaration = declaration
        self.docname = docname
        self.isRedeclaration = False
        self._assert_invariants()

        # Remember to modify Symbol.remove if modifications to the parent change.
        self._children = []  # type: List[Symbol]
        self._anonChildren = []  # type: List[Symbol]
        # note: _children includes _anonChildren
        if self.parent:
            self.parent._children.append(self)
        if self.declaration:
            self.declaration.symbol = self
        # add symbols for the template params
        # (do it after self._children has been initialised
        if self.templateParams:
            for p in self.templateParams.params:
                if not p.get_identifier():
                    continue
                # only add a declaration if we our selfs are from a declaration
                if declaration:
                    decl = ASTDeclaration('templateParam', None, None, p)
                else:
                    decl = None
                nne = ASTNestedNameElement(p.get_identifier(), None)
                nn = ASTNestedName([nne], [False], rooted=False)
                self._add_symbols(nn, [], decl, docname)
        # add symbols for function parameters, if any
        if declaration is not None and declaration.function_params is not None:
            for p in declaration.function_params:
                if p.arg is None:
                    continue
                nn = p.arg.name
                if nn is None:
                    continue
                # (comparing to the template params: we have checked that we are a declaration)
                decl = ASTDeclaration('functionParam', None, None, p)
                assert not nn.rooted
                assert len(nn.names) == 1
                identOrOp = nn.names[0].identOrOp
                Symbol(parent=self, identOrOp=identOrOp,
                       templateParams=None, templateArgs=None,
                       declaration=decl, docname=docname)