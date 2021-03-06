from collections import OrderedDict

try:
    from gnupg import GPG
except:
    from sleekxmpp.thirdparty.gnupg import GPG

from sleekxmpp.thirdparty import socks
from sleekxmpp.thirdparty.mini_dateutil import tzutc, tzoffset, parse_iso
from sleekxmpp.thirdparty.orderedset import OrderedSet
