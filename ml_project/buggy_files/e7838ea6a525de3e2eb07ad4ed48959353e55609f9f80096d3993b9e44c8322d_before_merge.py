    def run(self, project, options):
        """
        Run a one-off command on a service.

        For example:

            $ docker-compose run web python manage.py shell

        By default, linked services will be started, unless they are already
        running. If you do not want to start linked services, use
        `docker-compose run --no-deps SERVICE COMMAND [ARGS...]`.

        Usage: run [options] [-e KEY=VAL...] SERVICE [COMMAND] [ARGS...]

        Options:
            --allow-insecure-ssl  Allow insecure connections to the docker
                                  registry
            -d                    Detached mode: Run container in the background, print
                                  new container name.
            --entrypoint CMD      Override the entrypoint of the image.
            -e KEY=VAL            Set an environment variable (can be used multiple times)
            --no-deps             Don't start linked services.
            --rm                  Remove container after run. Ignored in detached mode.
            --service-ports       Run command with the service's ports enabled and mapped
                                  to the host.
            -T                    Disable pseudo-tty allocation. By default `docker-compose run`
                                  allocates a TTY.
        """
        service = project.get_service(options['SERVICE'])

        insecure_registry = options['--allow-insecure-ssl']

        if not options['--no-deps']:
            deps = service.get_linked_names()

            if len(deps) > 0:
                project.up(
                    service_names=deps,
                    start_links=True,
                    recreate=False,
                    insecure_registry=insecure_registry,
                    detach=options['-d']
                )

        tty = True
        if options['-d'] or options['-T'] or not sys.stdin.isatty():
            tty = False

        if options['COMMAND']:
            command = [options['COMMAND']] + options['ARGS']
        else:
            command = service.options.get('command')

        container_options = {
            'command': command,
            'tty': tty,
            'stdin_open': not options['-d'],
            'detach': options['-d'],
        }

        if options['-e']:
            for option in options['-e']:
                if 'environment' not in service.options:
                    service.options['environment'] = {}
                k, v = option.split('=', 1)
                service.options['environment'][k] = v

        if options['--entrypoint']:
            container_options['entrypoint'] = options.get('--entrypoint')
        container = service.create_container(
            one_off=True,
            insecure_registry=insecure_registry,
            **container_options
        )

        service_ports = None
        if options['--service-ports']:
            service_ports = service.options['ports']
        if options['-d']:
            service.start_container(container, ports=service_ports, one_off=True)
            print(container.name)
        else:
            service.start_container(container, ports=service_ports, one_off=True)
            dockerpty.start(project.client, container.id, interactive=not options['-T'])
            exit_code = container.wait()
            if options['--rm']:
                log.info("Removing %s..." % container.name)
                project.client.remove_container(container.id)
            sys.exit(exit_code)