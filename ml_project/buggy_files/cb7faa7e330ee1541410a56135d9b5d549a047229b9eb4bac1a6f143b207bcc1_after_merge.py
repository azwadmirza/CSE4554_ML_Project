def main(argv):
    parser = argparse.ArgumentParser(add_help=False, description=('Tunnel helper script, starts a (hidden) tunnel as a service'))
    parser.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    parser.add_argument('--ipv8_port', '-d', default=-1, type=int, help='IPv8 port', action=PortAction, metavar='{0..65535}')
    parser.add_argument('--ipv8_address', '-i', default='0.0.0.0', type=str, help='IPv8 listening address', action=IPAction)
    parser.add_argument('--ipv8_bootstrap_override', '-b', default=None, type=str,
                        help='Force the usage of specific IPv8 bootstrap server (ip:port)', action=IPPortAction)
    parser.add_argument('--restapi', '-p', default=52194, type=str,
                        help='Use an alternate port for the REST API', action=PortAction, metavar='{0..65535}')
    parser.add_argument('--cert-file', '-e', help='Path to combined certificate/key file. If not given HTTP is used.')
    parser.add_argument('--api-key', '-k', help='API key to use. If not given API key protection is disabled.')
    parser.add_argument('--random_slots', '-r', default=10, type=int, help='Specifies the number of random slots')
    parser.add_argument('--competing_slots', '-c', default=20, type=int, help='Specifies the number of competing slots')
    
    parser.add_argument('--exit', '-x', action='store_const', default=False, const=True, help='Allow being an exit-node')
    parser.add_argument('--testnet', '-t', action='store_const', default=False, const=True, help='Join the testnet')
    parser.add_argument('--no-rest-api', '-a', action='store_const', default=False, const=True, help='Disable the REST api')
    parser.add_argument('--log-rejects', action='store_const', default=False, const=True, help='Log rejects')
    parser.add_argument('--log-circuits', action='store_const', default=False, const=True, help='Log information about circuits')

    args = parser.parse_args(sys.argv[1:])    
    service = TunnelHelperService()
    
    loop = get_event_loop()
    coro = service.start(args)
    ensure_future(coro)
    
    if sys.platform == 'win32':
        # Unfortunately, this is needed on Windows for Ctrl+C to work consistently.
        # Should no longer be needed in Python 3.8.
        async def wakeup():
            while True:
                await sleep(1)
        ensure_future(wakeup())
    
    loop.run_forever()