def calculate_class_mro(defn: ClassDef, fail: Callable[[str, Context], None]) -> None:
    try:
        defn.info.calculate_mro()
    except MroError:
        fail("Cannot determine consistent method resolution order "
             '(MRO) for "%s"' % defn.name, defn)
        defn.info.mro = []