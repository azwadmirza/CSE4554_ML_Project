def send_msg(msg, server='localhost', port='6667', channel=None, nick_to=None, key=None, topic=None,
             nick="ansible", color='none', passwd=False, timeout=30, use_ssl=False, part=True, style=None):
    '''send message to IRC'''
    nick_to = [] if nick_to is None else nick_to

    colornumbers = {
        'white': "00",
        'black': "01",
        'blue': "02",
        'green': "03",
        'red': "04",
        'brown': "05",
        'purple': "06",
        'orange': "07",
        'yellow': "08",
        'light_green': "09",
        'teal': "10",
        'light_cyan': "11",
        'light_blue': "12",
        'pink': "13",
        'gray': "14",
        'light_gray': "15",
    }

    stylechoices = {
        'bold': "\x02",
        'underline': "\x1F",
        'reverse': "\x16",
        'italic': "\x1D",
    }

    try:
        styletext = stylechoices[style]
    except:
        styletext = ""

    try:
        colornumber = colornumbers[color]
        colortext = "\x03" + colornumber
    except:
        colortext = ""

    message = styletext + colortext + msg

    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if use_ssl:
        irc = ssl.wrap_socket(irc)
    irc.connect((server, int(port)))
    if passwd:
        irc.send('PASS %s\r\n' % passwd)
    irc.send('NICK %s\r\n' % nick)
    irc.send('USER %s %s %s :ansible IRC\r\n' % (nick, nick, nick))
    motd = ''
    start = time.time()
    while 1:
        motd += irc.recv(1024)
        # The server might send back a shorter nick than we specified (due to NICKLEN),
        #  so grab that and use it from now on (assuming we find the 00[1-4] response).
        match = re.search(r'^:\S+ 00[1-4] (?P<nick>\S+) :', motd, flags=re.M)
        if match:
            nick = match.group('nick')
            break
        elif time.time() - start > timeout:
            raise Exception('Timeout waiting for IRC server welcome response')
        time.sleep(0.5)

    if key:
        irc.send('JOIN %s %s\r\n' % (channel, key))
    else:
        irc.send('JOIN %s\r\n' % channel)

    join = ''
    start = time.time()
    while 1:
        join += irc.recv(1024)
        if re.search(r'^:\S+ 366 %s %s :' % (nick, channel), join, flags=re.M):
            break
        elif time.time() - start > timeout:
            raise Exception('Timeout waiting for IRC JOIN response')
        time.sleep(0.5)

    if topic is not None:
        irc.send('TOPIC %s :%s\r\n' % (channel, topic))
        time.sleep(1)

    if nick_to:
        for nick in nick_to:
            irc.send('PRIVMSG %s :%s\r\n' % (nick, message))
    if channel:
        irc.send('PRIVMSG %s :%s\r\n' % (channel, message))
    time.sleep(1)
    if part:
        irc.send('PART %s\r\n' % channel)
        irc.send('QUIT\r\n')
        time.sleep(1)
    irc.close()