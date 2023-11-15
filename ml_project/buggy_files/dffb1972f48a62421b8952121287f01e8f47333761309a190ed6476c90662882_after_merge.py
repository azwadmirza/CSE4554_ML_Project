    def check_nested_import(self, node: AnyImport) -> None:
        parent = getattr(node, 'wps_parent', None)
        if parent is not None and not isinstance(parent, ast.Module):
            self._error_callback(NestedImportViolation(node))