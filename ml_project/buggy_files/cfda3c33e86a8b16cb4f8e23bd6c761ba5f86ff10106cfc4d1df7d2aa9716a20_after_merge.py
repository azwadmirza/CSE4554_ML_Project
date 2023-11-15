def get_device():
    """ If Cuda is available, use Cuda device, else use CPU device
        When choosing from Cuda devices, this function will choose the one with max memory available

    Returns: string device name

    """
    # TODO: could use gputil in the future
    device = 'cpu'
    if torch.cuda.is_available():
        smi_out = os.popen('nvidia-smi -q -d Memory | grep -A4 GPU|grep Free').read()
        # smi_out=
        #       Free                 : xxxxxx MiB
        #       Free                 : xxxxxx MiB
        #                      ....
        visable_list = [int(x) for x in os.getenv('CUDA_VISIBLE_DEVICES', '').split(',')]
        memory_available = [int(x.split()[2]) for x in smi_out.splitlines()]
        for cuda_index,_ in enumerate(memory_available):
            if cuda_index not in visable_list and visable_list:
                memory_available[cuda_index] = 0

        if memory_available:
            if max(memory_available) != 0:
                device = 'cuda:' + str(memory_available.index(max(memory_available)))
    return device