def parse_format(xml_file):
    """Parse the xml file to create types, scaling factor types, and scales.
    """
    tree = ElementTree()
    tree.parse(xml_file)

    for param in tree.find("parameters").getchildren():
        VARIABLES[param.get("name")] = param.get("value")

    types_scales = {}

    for prod in tree.find("product"):
        ascii = (prod.tag in ["mphr", "sphr"])
        res = []
        for i in prod:
            lres = CASES[i.tag](i, ascii)
            if lres is not None:
                res.append(lres)
        types_scales[(prod.tag, int(prod.get("subclass")))] = res

    types = {}
    stypes = {}
    scales = {}

    for key, val in types_scales.items():
        types[key] = to_dtype(val)
        stypes[key] = to_scaled_dtype(val)
        scales[key] = to_scales(val)

    return types, stypes, scales