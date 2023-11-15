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

        # Do symbol addition after self._children has been initialised.
        self._add_template_and_function_params()