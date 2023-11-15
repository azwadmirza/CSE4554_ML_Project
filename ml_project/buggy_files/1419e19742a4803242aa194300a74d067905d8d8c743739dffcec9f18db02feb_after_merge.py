    def __new__(cls):
        return ClosedNamespace.__new__(cls, "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              terms=[
                # Syntax Names
                "RDF", "Description", "ID", "about", "parseType",
                "resource", "li", "nodeID", "datatype",

                # RDF Classes
                "Seq", "Bag", "Alt", "Statement", "Property",
                "List", "PlainLiteral",

                # RDF Properties
                "subject", "predicate", "object", "type",
                "value", "first", "rest",
                # and _n where n is a non-negative integer

                # RDF Resources
                "nil",

                # Added in RDF 1.1
                "XMLLiteral", "HTML", "langString"]
        )