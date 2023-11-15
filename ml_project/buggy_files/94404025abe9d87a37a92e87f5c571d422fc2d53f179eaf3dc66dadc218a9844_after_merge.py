    def get_item_name_and_attributes(self, item, attributes):
        if isinstance(item, ast.Name):
            return item.id, attributes
        elif isinstance(item, ast.AnnAssign):
            return self.get_item_name_and_attributes(item.annotation, attributes)
        elif isinstance(item, ast.Subscript):
            return self.get_item_name_and_attributes(item.value, attributes)
        elif isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == 'map':
            if len(item.args) != 2:
                raise StructureException("Map type expects two type arguments map(type1, type2)", item.func)
            return self.get_item_name_and_attributes(item.args, attributes)
        # elif ist
        elif isinstance(item, ast.Call) and isinstance(item.func, ast.Name):
            attributes[item.func.id] = True
            # Raise for multiple args
            if len(item.args) != 1:
                raise StructureException("%s expects one arg (the type)" % item.func.id)
            return self.get_item_name_and_attributes(item.args[0], attributes)
        return None, attributes