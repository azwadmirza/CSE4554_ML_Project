        def onMissingQualifiedSymbol(parentSymbol, identOrOp, templateParams, templateArgs):
            # type: (Symbol, Union[ASTIdentifier, ASTOperator], Any, ASTTemplateArgs) -> Symbol
            if Symbol.debug_lookup:
                print("   _add_symbols, onMissingQualifiedSymbol:")
                print("      templateParams:", templateParams)
                print("      identOrOp:     ", identOrOp)
                print("      templateARgs:  ", templateArgs)
            return Symbol(parent=parentSymbol, identOrOp=identOrOp,
                          templateParams=templateParams,
                          templateArgs=templateArgs, declaration=None,
                          docname=None)