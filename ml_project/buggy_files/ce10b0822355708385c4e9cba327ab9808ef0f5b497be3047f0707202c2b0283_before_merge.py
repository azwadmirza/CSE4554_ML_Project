def strip_target(node: Union[MypyFile, FuncItem, OverloadedFuncDef]) -> None:
    """Reset a fine-grained incremental target to state after semantic analysis pass 1.

    NOTE: Currently we opportunistically only reset changes that are known to otherwise
        cause trouble.
    """
    visitor = NodeStripVisitor()
    if isinstance(node, MypyFile):
        visitor.strip_file_top_level(node)
    else:
        node.accept(visitor)