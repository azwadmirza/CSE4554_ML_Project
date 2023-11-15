def read_tokens(filename, label_dict):
    """Read tokens as a sequence of sentences

    :param str filename : The name of the input file
    :param dict label_dict : dictionary that maps token label string to its ID number
    :return list of ID sequences
    :rtype list
    """

    data = []
    unk = label_dict['<unk>']
    for ln in tqdm(open(filename, 'r', encoding='utf-8')):
        data.append(np.array([label_dict.get(label, unk) for label in ln.split()], dtype=np.int32))
    return data