def setup_documenters(app: Any) -> None:
    from sphinx.ext.autodoc import (AttributeDocumenter, ClassDocumenter, DataDocumenter,
                                    DecoratorDocumenter, ExceptionDocumenter,
                                    FunctionDocumenter, GenericAliasDocumenter,
                                    InstanceAttributeDocumenter, MethodDocumenter,
                                    ModuleDocumenter, PropertyDocumenter,
                                    SingledispatchFunctionDocumenter, SlotsAttributeDocumenter)
    documenters = [
        ModuleDocumenter, ClassDocumenter, ExceptionDocumenter, DataDocumenter,
        FunctionDocumenter, MethodDocumenter, AttributeDocumenter,
        InstanceAttributeDocumenter, DecoratorDocumenter, PropertyDocumenter,
        SlotsAttributeDocumenter, GenericAliasDocumenter, SingledispatchFunctionDocumenter,
    ]  # type: List[Type[Documenter]]
    for documenter in documenters:
        app.registry.add_documenter(documenter.objtype, documenter)