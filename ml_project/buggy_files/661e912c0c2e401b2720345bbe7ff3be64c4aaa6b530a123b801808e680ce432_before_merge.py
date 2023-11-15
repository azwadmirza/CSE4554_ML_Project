def robust_connect_subscriber(conn, dest_addr, dest_port, pub_uri, receive_cb, resolved_topic_name):
    """
    Keeps trying to create connection for subscriber.  Then passes off to receive_loop once connected.
    """
    # kwc: this logic is not very elegant.  I am waiting to rewrite
    # the I/O loop with async i/o to clean this up.
    
    # timeout is really generous. for now just choosing one that is large but not infinite
    interval = 0.5
    while conn.socket is None and not conn.done and not rospy.is_shutdown():
        try:
            conn.connect(dest_addr, dest_port, pub_uri, timeout=60.)
        except rospy.exceptions.TransportInitError as e:
            rospyerr("unable to create subscriber transport: %s.  Will try again in %ss", e, interval)
            interval = interval * 2
            time.sleep(interval)
            
            # check to see if publisher state has changed
            conn.done = not check_if_still_publisher(resolved_topic_name, pub_uri)
	
    if not conn.done:
        conn.receive_loop(receive_cb)	    