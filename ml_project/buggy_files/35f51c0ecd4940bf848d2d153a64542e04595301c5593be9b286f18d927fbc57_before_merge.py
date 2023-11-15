    def perform_mutation(cls, _root, info, menu, moves):
        _type, menu_id = from_global_id(menu)  # type: str, int
        assert _type == "Menu", "Expected a menu of type Menu"

        operations = cls.clean_moves(info, menu_id, moves)

        for operation in operations:
            cls.perform_operation(operation)

        return cls(menu=models.Menu.objects.get(pk=menu_id))