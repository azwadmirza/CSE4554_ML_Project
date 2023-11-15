        def onMissingQualifiedSymbol(parentSymbol, identOrOp, templateParams, templateArgs):
            # type: (Symbol, Union[ASTIdentifier, ASTOperator], Any, ASTTemplateArgs) -> Symbol
            return Symbol(parent=parentSymbol, identOrOp=identOrOp,
                          templateParams=templateParams,
                          templateArgs=templateArgs, declaration=None,
                          docname=None)