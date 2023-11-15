def start_container(image_tag_string):
    '''Start the test container in detach state'''
    try:
        client.containers.run(image_tag_string, name=container, detach=True)
    except requests.exceptions.HTTPError:
        # container may already be running
        pass
    try:
        remove_container()
        client.containers.run(image_tag_string, name=container, detach=True)
    except requests.exceptions.HTTPError:
        # not sure what the error is now
        raise Exception("Cannot remove running container")