def get_device():
    """ If Cuda is available, use Cuda device, else use CPU device
        When choosing from Cuda devices, this function will choose the one with max memory available

    Returns: string device name

    """
    # TODO: could use gputil in the future
    if torch.cuda.is_available():
        smi_out = os.popen('nvidia-smi -q -d Memory | grep -A4 GPU|grep Free').read()
        # smi_out=
        #       Free                 : xxxxxx MiB
        #       Free                 : xxxxxx MiB
        #                      ....
        memory_available = [int(x.split()[2]) for x in smi_out.splitlines()]
        if not memory_available:
            device = 'cpu'
        else:
            device = 'cuda:' + str(memory_available.index(max(memory_available)))
    else:
        device = 'cpu'
    return device