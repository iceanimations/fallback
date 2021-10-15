
__all__ = ['Texture', 'Episode', 'Sequence', 'Shot', 'Season']

from pyasm.search import *
import re, time, json


class Season():
    # parent_stype = Search('vfx/season')
    append = 'S'


class Texture:
    pass

class Episode(SObject):
    parent_column = ''
    def commit(my, *args, **kwargs):

        with open('/home/apache/logger.log', 'a') as f:

            f.write(json.dumps(my.get_data(), indent = 2))

        my_code = my.get_value('code')
        search = Search(my.get_search_type())

        if ((my.force_insert or my.get_id() in [-1, '-1', '']) and
            my_code):

            if (my.generate_code(my_code) in
                [sobj.get('code')
                 for sobj in search.get_sobjects()]):

                raise SObjectException('%s already exists'
                                       %my.generate_code(my_code))

            my.regex = '^([1-9]\d*)(\_[a-z])?$'

            if re.match(my.regex, my_code):
                my_gen_code = my.generate_code(my_code)
                my.set_value('code', my_gen_code)
                super(Episode, my).commit(*args, **kwargs)

            else:

                raise SObjectException('The format in which the code was '+
                                       'entered is not valid. '+
                                       'Please contact the technical dept.')
        elif ((my.force_insert or my.get_id() not in [-1, '-1', '']) and
        my_code == my.get_prev_data('code') and
        my.get_prev_data(my.parent_column) == my.get(my.parent_column) if my.parent_column else True):

            super(Episode, my).commit(*args, **kwargs)

        raise SObjectException('The format in which the code was '+
                                       'entered is not valid. '+
                                       'Please contact the technical dept.')

    def generate_code(my, code):

        return 'E' + str(code).zfill(2)


class Sequence(Episode):

    parent_stype = Search('vfx/episode')
    append = 'SQ'
    parent_column = 'episode_code'

    def generate_code(my, code):

        parent = my.get_value(my.parent_column)

        if parent:
            return parent + "_%s%s" %(my.append,
                                       str(code).zfill(3))

        else:
            raise SObject('Parent not defined.')

class Shot(Sequence):

    parent_stype = Search('vfx/sequence')
    append = 'SH'
    parent_column = 'sequence_code'
