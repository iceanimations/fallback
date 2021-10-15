import app.util as util
from auth import user as USER
reload(util)


def checkinability(search_key, process = None, context = None, user = None):

    '''
    @search_key: the search_key of the sobject whose checkinability
    is to be checked
    @context: context with which the checkin is to be made
    not considered yet
    @return: True if the user can checkin the file
    '''

    server = USER.get_server()
    if not user:
        user = USER.get_user()

    if user == 'admin':
        return True


    logins = server.query('sthpw/login_in_group', filters = [('login', user)])

    if logins:
        for login in logins[:]:
            groups =  server.query('sthpw/login_group',
                                   filters = [('login_group',
                                               login['login_group'])])
            if not groups:
                continue

            project = groups[0]['project_code']
            sk_project = util.get_project_from_search_key(search_key)
            if ((project == sk_project
                 or sk_project in groups[0]['login_group']) and

                # modeling and rigging dept can checkin to asset
                ('/asset' in search_key and
                 any([dpt in login['login_group'] for dpt in ['model',
                                                              'rig',
                                                              'light']])) or
                # animation dept can checkin to shot
                ('/shot' in search_key and
                 any([dpt in login['login_group'] for dpt in ['animation',
                                                                'light',
                                                                'vfx']]))):

                return True

            if any([sup in groups[0]['login_group'] for sup in ['supervisor',
                                                                'admin']]):

                return True


    return False
