    def __init__(self, ref, conanfile, context, recipe=None, path=None):
        self.ref = ref
        self.path = path  # path to the consumer conanfile.xx for consumer, None otherwise
        self._package_id = None
        self.prev = None
        self.conanfile = conanfile
        self.dependencies = []  # Ordered Edges
        self.dependants = set()  # Edges
        self.binary = None
        self.recipe = recipe
        self.remote = None
        self.binary_remote = None
        self.revision_pinned = False  # The revision has been specified by the user
        self.context = context

        # A subset of the graph that will conflict by package name
        self._public_deps = _NodeOrderedDict()  # {ref.name: Node}
        # all the public deps only in the closure of this node
        # The dependencies that will be part of deps_cpp_info, can't conflict
        self._public_closure = _NodeOrderedDict()  # {ref.name: Node}
        # The dependencies of this node that will be propagated to consumers when they depend
        # on this node. It includes regular (not private and not build requires) dependencies
        self._transitive_closure = OrderedDict()
        self.inverse_closure = set()  # set of nodes that have this one in their public
        self._ancestors = _NodeOrderedDict()  # set{ref.name}
        self._id = None  # Unique ID (uuid at the moment) of a node in the graph
        self.graph_lock_node = None  # the locking information can be None
        self.id_direct_prefs = None
        self.id_indirect_prefs = None