try:
    from ldap_authenticate import *
except:
    pass

import checkin_permission as cp
reload(cp)

from checkin_permission import *
