def render_statement(ostream, match, statement, indent=0):
    ostream.write("  " * indent)
    if statement["type"] in ("and", "or", "optional"):
        ostream.write(statement["type"])
        ostream.writeln(":")
    elif statement["type"] == "not":
        # this statement is handled specially in `render_match` using the MODE_SUCCESS/MODE_FAILURE flags.
        ostream.writeln("not:")
    elif statement["type"] == "some":
        ostream.write("%d or more" % (statement["count"]))
        ostream.writeln(":")
    elif statement["type"] == "range":
        # `range` is a weird node, its almost a hybrid of statement+feature.
        # it is a specific feature repeated multiple times.
        # there's no additional logic in the feature part, just the existence of a feature.
        # so, we have to inline some of the feature rendering here.

        child = statement["child"]

        if child[child["type"]]:
            value = rutils.bold2(child[child["type"]])
            if child.get("description"):
                ostream.write("count(%s(%s = %s)): " % (child["type"], value, child["description"]))
            else:
                ostream.write("count(%s(%s)): " % (child["type"], value))
        else:
            ostream.write("count(%s): " % child["type"])

        if statement["max"] == statement["min"]:
            ostream.write("%d" % (statement["min"]))
        elif statement["min"] == 0:
            ostream.write("%d or fewer" % (statement["max"]))
        elif statement["max"] == (1 << 64 - 1):
            ostream.write("%d or more" % (statement["min"]))
        else:
            ostream.write("between %d and %d" % (statement["min"], statement["max"]))

        render_locations(ostream, match)
        ostream.write("\n")
    elif statement["type"] == "subscope":
        ostream.write(statement["subscope"])
        ostream.writeln(":")
    else:
        raise RuntimeError("unexpected match statement type: " + str(statement))