def deserialize_graph(ser_graph, graph_cls=None):
    from google.protobuf.message import DecodeError
    from .serialize.protos.graph_pb2 import GraphDef
    from .graph import DirectedGraph
    graph_cls = graph_cls or DirectedGraph
    ser_graph_bin = to_binary(ser_graph)
    g = GraphDef()
    try:
        g.ParseFromString(ser_graph_bin)
        return graph_cls.from_pb(g)
    except DecodeError:
        pass

    try:
        ser_graph_bin = zlib.decompress(ser_graph_bin)
        g.ParseFromString(ser_graph_bin)
        return graph_cls.from_pb(g)
    except (zlib.error, DecodeError):
        pass

    json_obj = json.loads(to_str(ser_graph))
    return graph_cls.from_json(json_obj)