def node_labels(name, **kwargs):
    '''
    Return the labels of the node identified by the specified name

    CLI Examples::

        salt '*' kubernetes.node_labels name="minikube"
    '''
    match = node(name, **kwargs)

    if match is not None:
        return match['metadata']['labels']

    return {}