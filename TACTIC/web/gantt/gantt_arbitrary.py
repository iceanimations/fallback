from tactic.ui.table import GanttElementWdg as gantt
from pyasm.search import SObject, Search, SearchKey, SearchType
from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, WebContainer, Table
from pyasm.widget import HiddenWdg, TextWdg, IconWdg
from pyasm.common import Date, jsonloads, jsondumps, TacticException
from pyasm.command import DatabaseAction, Command
from pyasm.biz import ExpressionParser

from tactic.ui.widget import IconButtonWdg

import datetime
from dateutil import rrule
from dateutil import parser

class MyGantt(gantt):

    def __init__(my, *args, **kwargs):
        # search_type = "vfx/shot"
        # my.sobjects = SObject(search_type)
        # my.search = Search(search_type)
        
        
        my.ARGS_KEYS["search_key"] = "something"
        super(MyGantt, my).__init__(*args, **kwargs)
        my.preprocess()
        # my.property_list[0]["start_date_expr"] = my.kwargs["start_date"]
        # my.property_list[0]["end_date_expr"] = my.kwargs["end_date"]
        my.kwargs = eval(my.kwargs["kwarg"])
        my.options = "["+repr(my.kwargs["options"])+"]"
        print "options: ", my.options

        

    # ARGS_KEYS = {
    # 'show_title' : {
    #     'description': 'true|false Determines whether the show title can be seen',
    #     'type': 'CheckboxWdg',
    #     'order': 0,
    #     'category': 'Display'
    # },
    # 'options': {
    #     'type': 'TextAreaWdg',
    #     'description': 'A list of options for the various gantt bars',
    #     'order': 3,
    #     'category': 'Config'
    # },
    # 'range_start_date': {
    #     'type': 'CalendarInputWdg',
    #     'description': 'The start date of the gantt widget',
    #     'order': 2,
    #     'category': 'Display'
    # },
    # 'range_end_date': {
    #     'type': 'CalendarInputWdg',
    #     'description': 'The end date of the gantt widget',
    #     'order': 3,
    #     'category': 'Display'
    # },
    # 'overlap': {
    #     'type': 'SelectWdg',
    #     'description': 'determines whether or not to overlap date ranges',
    #     'order': 5,
    #     'values': 'true|false',
    #     'category': 'Display',
    # },
    # 'date_mode': {
    #     'type': 'SelectWdg',
    #     'description': 'The display modes for the dates: visible means that the dates are always visible, while hover means that the dates will only appear when hovering over the cell',
    #     'values': 'visible|hover|none',
    #     'order': 1,
    #     'category': 'Display'
    # },
    # 'show_milestones': {
    #     'type': 'SelectWdg',
    #     'description': 'Determines which milestones to show for each task',
    #     'values': 'task|project',
    #     'order': 3,
    #     'category': 'Display'
    # },
    # 'year_display': {
    #     'type': 'SelectWdg',
    #     'description': 'Determines whether or not to show the year',
    #     'values': 'none|default',
    #     'order': 4,
    #     'category': 'Display'
    # },
    # 'week_display': {
    #     'type': 'SelectWdg',
    #     'description': 'Determines whether or not to show the week',
    #     'values': 'none|default',
    #     'order': 5,
    #     'category': 'Display'
    # },
    # 'week_start': {
    #     'type': 'SelectWdg',
    #     'description': 'Day the week starts',
    #     'labels': 'MO|TU|WE|TH|FR|SA|SU',
    #     'values': '0|1|2|3|4|5|6',
    #     'order': 6,
    #     'category': 'Display'
    # },
    # 'bar_height': {
    #     'type': 'SelectWdg',
    #     'description': 'Determines the height of the bars',
    #     'values': '6|12|18|24',
    #     'order': 7,
    #     'category': 'Display'
    # },
    # 'color_mode': {
    #     'type': 'SelectWdg',
    #     'description': 'Special color mode for display of tasks',
    #     'values': 'status|process',
    #     'order': 8,
    #     'category': 'Display'
    # },
    # 'search_key':{
    #     'type': 'TextAreaWdg',
    #     'description': 'Search key of the sobject to be displayed',
    #     'order': 3,
    #     'category': 'Config'
    # },
    # }

        

    def get_display(my):
        
        
        my.preprocess()
        top = DivWdg()
        top.add_class("spt_gantt_top")

        # this is for storing of all the data for GanttCbk
        value_wdg = HiddenWdg('gantt_data')
        #value_wdg = TextWdg('gantt_data')
        #value_wdg.add_style("width: 400px")
        value_wdg.add_class("spt_gantt_data")
        top.add(value_wdg)

        # set the initial values
        data = {
            '_range_start_date': my.start_date.strftime("%Y-%m-%d"),
            '_range_end_date': my.end_date.strftime("%Y-%m-%d"),
            '_offset': my.offset_width,
            '_width': my.total_width
        }
        # Need to set form value to false so that this info is not reused
        # on insert when draw FastTable.  This is probably a vestigial
        # feature to have set_value set the form value.
        value_wdg.set_value( jsondumps(data).replace('"', "&quot;"), set_form_value=False )


        # dummy for triggering the display of Commit button
        value_wdg = HiddenWdg(my.get_name())
        value_wdg.add_class("spt_gantt_value")
        top.add( value_wdg )

        top.add_style("margin: -3px")
 

        outer_div = DivWdg()
        top.add(outer_div)


        outer_div.add_class("spt_table_scale")
        outer_div.add_style("width: %s" % my.visible_width)
        outer_div.add_style("overflow: hidden")
        inner_div = DivWdg()
        inner_div.add_class("spt_gantt_scroll")
        inner_div.add_style("width: %s" % my.total_width)
        inner_div.add_style("margin-left: %s" % my.offset_width)
        inner_div.add_style("position: relative")
        outer_div.add(inner_div)
        inner_div.add_style("overflow: hidden")
        outer_div.add_class("spt_resizable")


        # draw the day widgets
        day_wdg = my.get_special_day_wdg()
        inner_div.add( day_wdg )


        height = my.kwargs.get("bar_height");
        if not height:
            height = 12
        else:
            height = int(height)



        #outer_div.add_style("height: 0%")
        outer_div.add_style("position: relative")
        outer_div.add_style("height: 100%")
        #inner_div.add_style("position: absolute")
        inner_div.add_style("min-height: %spx" % (height+6))

        # draw the dividers
        divider_wdg = my.get_divider_wdg()
        inner_div.add( divider_wdg )



        my.overlap = my.kwargs.get("overlap")
        if my.overlap in [True, "true"]:
            my.overlap = True
        else:
            my.overlap = False


        for index, properties in enumerate(my.property_list):
            color_results = my.color_results[index]
            color = None # color_results.get(sobject.get_search_key())
            if not color:
                color = properties.get("color")
                if not color:
                    color = "#555"

            key = properties.get('key')
            if not key:
                key = index

            editable = properties.get('edit')
            if editable != 'false':
                editable = True
            else:
                editable = False
            if my.overlap:
                editable = False

            default = properties.get('default')




            # sobject = my.get_current_sobject()
            # search_key = my.get_option("search_key")
            
            # print "search_key random: ", my.property_list
            print "="*30,"\n", "="*30

            print "kwargs: ", my.kwargs
            print "property: ", my.property_list
            # print "options: ", my.options
            # print "ARGS_OPTIONS: ", my.ARGS_OPTIONS
            # print "ATTRS: ", my.attrs
            # print "input: ", my.input
            # print "args_keys: ", my.get_args_keys()
            # print "my.dir: ", dir(my)
            # print "my.get_parent_view: ", repr(my.get_parent_view())
            # print "my.get_parent_wdg: ", repr(my.get_parent_wdg())
            # print "123"*10**7
            print "="*30, "\n", "="*30
            # search_key = "vfx/shot?project=vfx&code=S01_001"
            # my.property_list[0]["end_date_expr"] = my.kwargs["end_date"]
            # my.property_list[0]["start_date_expr"] = my.kwargs["start_date"]
            search_key = my.kwargs["kwarg"]
            # if not search_key:
            #     raise Exception
            sobject = SearchKey.get_by_search_key(search_key)
            sobject_data = my.range_data.get(search_key)
            if sobject_data:
                sobject_data = sobject_data[index]
            if not sobject_data:
                sobject_data = []


            # get the data about the days in the range
            day_data = sobject.get_value("data", no_exception=True)
            if not day_data:
                day_data = {}
            else:
                day_data = jsonloads(day_data)


            for range_data in sobject_data:

                if range_data.get("color"):
                    cur_color = range_data.get("color")
                else:
                    cur_color = color

                bar = my.draw_bar(index, key, cur_color, editable, default=default, height=height, range_data=range_data, day_data=day_data)
                bar.add_style("z-index: 2")
                bar.add_style("position: absolute")
                bar.add_style("padding-top: 2px")
                bar.add_style("padding-bottom: 2px")
                #bar.add_style("border: solid 1px red")

                if not my.has_start_date and my.hide_bar:
                    pass
                else:
                    inner_div.add(bar)

                if not my.overlap:
                    inner_div.add("<br clear='all'>")
                else:
                    inner_div.add("<br class='spt_overlap' style='display: none' clear='all'>")


        #if not my.overlap:
        #    inner_div.add("<br clear='all'/>")
        return top
