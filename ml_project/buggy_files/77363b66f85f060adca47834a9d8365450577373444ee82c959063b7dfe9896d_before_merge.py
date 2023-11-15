def auto_suggest_network(dataset, net):
    if isinstance(dataset, str):
        dataset_name = dataset
    elif isinstance(dataset, AutoGluonObject):
        if 'name' in dataset.kwargs:
            dataset_name = dataset.kwargs['name']
        else:
            return net
    else:
        return net
    dataset_name = dataset_name.lower()
    if 'mnist' in dataset_name:
        if isinstance(net, str) or isinstance(net, Categorical):
            net = mnist_net()
            logger.info('Auto suggesting network net for dataset {}'.format(net, dataset_name))
            return net
    elif 'cifar' in dataset_name:
        if isinstance(net, str):
            if 'cifar' not in net:
                net = 'cifar_resnet20_v1'
        elif isinstance(net, Categorical):
            newdata = []
            for x in net.data:
                if 'cifar' in x:
                    newdata.append(x)
            net.data = newdata if len(newdata) > 0 else ['cifar_resnet20_v1', 'cifar_resnet56_v1']
        logger.info('Auto suggesting network net for dataset {}'.format(net, dataset_name))
        return net