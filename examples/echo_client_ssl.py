#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import os
import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
if sleekxmpp.__version_info__ < (1, 4, 0, '', 0):
    print('Expecting sleekxmpp version 1.4.0')
    exit(1)

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class EchoBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="--jid client@localhost # username to login")
    optp.add_option("-p", "--password", dest="password",
                    help="--password password # password for this jid")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(filename)-14s +%(lineno)-5s %(levelname)-5s %(message)s')

    if opts.jid is None:
        logging.critical('username@hostname is empty')
        logging.info(sys.argv[0] + ' -d' + ' -j client@localhost' + ' -p password')
        exit()
    else:
        if opts.password is None:
            logging.warning('password is empty')

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = EchoBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # If you are connecting to Facebook and wish to use the
    # X-FACEBOOK-PLATFORM authentication mechanism, you will need
    # your API key and an access token. Then you'll set:
    # xmpp.credentials['api_key'] = 'THE_API_KEY'
    # xmpp.credentials['access_token'] = 'THE_ACCESS_TOKEN'

    # If you are connecting to MSN, then you will need an
    # access token, and it does not matter what JID you
    # specify other than that the domain is 'messenger.live.com',
    # so '_@messenger.live.com' will work. You can specify
    # the access token as so:
    # xmpp.credentials['access_token'] = 'THE_ACCESS_TOKEN'

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    CERT_DIR='cert'
    xmpp.ca_certs = CERT_DIR + "/ca/root_ca.pem"
    xmpp.certfile = CERT_DIR + "/certs/client.pem"
    xmpp.keyfile  = CERT_DIR + "/certs/client.key"

    if os.path.isdir(CERT_DIR):
        if not os.path.isfile(xmpp.ca_certs):
            logging.critical('CA Certificate not found at %s' % xmpp.ca_certs)
            exit()
        if not os.path.isfile(xmpp.certfile):
            logging.error('Client Certificate not found at %s' % xmpp.certfile)
        if not os.path.isfile(xmpp.keyfile):
            logging.error('Client Key not found at %s' % xmpp.ca_certs)
    else:
        logging.critical('Certificate Directory not found at %s' % os.getcwd())
        exit()

    # Connect to the XMPP server and start processing XMPP stanzas.
    #if xmpp.connect(('127.0.0.1', 5222)):
    if xmpp.connect((xmpp._expected_server_name, 5222)):
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID.
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
