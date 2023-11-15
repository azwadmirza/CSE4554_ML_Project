async def demo(docker):
    try:
        await docker.images.get('alpine:latest')
    except DockerError as e:
        if e.status == 404:
            await docker.pull('alpine:latest')
        else:
            print('Error retrieving alpine:latest image.')
            return

    subscriber = docker.events.subscribe()

    config = {
        "Cmd": ["tail", "-f", "/var/log/dmesg"],
        "Image":"alpine:latest",
         "AttachStdin": False,
         "AttachStdout": True,
         "AttachStderr": True,
         "Tty": False,
         "OpenStdin": False,
         "StdinOnce": False,
    }
    container = await docker.containers.create_or_replace(
        config=config, name='testing')
    await container.start(config)
    print(f"=> created and started container {container._id[:12]}")

    while True:
        event = await subscriber.get()
        print(f"event: {event!r}")

        # Demonstrate simple event-driven container mgmt.
        if event['Actor']['ID'] == container._id:
            if event['Action'] == 'start':
                await container.stop()
                print(f"=> killed {container._id[:12]}")
            elif event['Action'] == 'stop':
                await container.delete(force=True)
                print(f"=> deleted {container._id[:12]}")
            elif event['Action'] == 'destroy':
                print('=> done with this container!')
                break