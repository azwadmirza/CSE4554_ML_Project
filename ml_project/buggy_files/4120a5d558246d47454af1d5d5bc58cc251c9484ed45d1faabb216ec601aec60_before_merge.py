def read_tokens(filename, label_dict):
    """Read tokens as a sequence of sentences

    :param str filename : The name of the input file
    :param dict label_dict : dictionary that maps token label string to its ID number
    :return list of ID sequences
    :rtype list
    """

    data = []
    for ln in open(filename, 'rb').readlines():
        data.append(np.array([label_dict[label]
                              if label in label_dict else label_dict['<unk>']
                              for label in ln.decode('utf-8').split()], dtype=np.int32))
    return data