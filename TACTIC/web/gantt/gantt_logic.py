import sys
from util import *
try:
    import tactic_capi_start as tcs
    _s = _server = tcs.server
except:
    from tactic_client_lib import TacticServerStub
    _s = _server = TacticServerStub.get()

try:
    from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, WebContainer, Table

    def make_bar(width, border_color = "white", height = 10,
                 border_style = "solid", bg = None,
                 b_radius = 3, border_width = 1, text = "",
                 styles = [], parent = None):
        bar = DivWdg()
        bar.add(text)
        map(bar.add_style, ["border-color: %s" %border_color,
                            "border-radius: %spx" %b_radius,
                            "border-style: %s" %border_style,
                            # "background-color: %s" %bg,
                            "border-width: %fpx"%border_width,
                            "height: %fpx" %height,
                            "width: %fpx" % round(width - 2 * border_width),
                            "text-align: center",
                            "opacity: 0.8"])
        map(bar.add_style, styles)
        
        if parent:
            parent.add(bar)
            
        return bar
    
    
    def make_calendar(start, end, width, height):

        disp_year = disp_month = disp_day = True
        
        s_year = float(start.year)
        e_year = float(end.year)
        s_month = float(start.month)
        e_month = float(end.month)
        s_day = float(start.day)
        e_day = float(end.day)
        years = e_year - s_year

        # if the start and end are in the same year no need
        # to display the years
        if years == 0:
            disp_year = False
        
        length = end - start
        days = length.days
        
        day_width = width/float(days)

        
        if day_width < 10: disp_day = False

        if e_month == s_month and years == 0:
            disp_month == False

        # the main calendar container
        main_cal = Table()
        map(main_cal.add_style, ("width: %spx" %width,))
        colors = ["red", "yellow", "blue", "green"]
        # add years
        if disp_year:

            calendar = get_table()
            main_cal.add_cell(calendar)
            
            _yr_wdth = year_width(start, end, width)
            for index, yr in enumerate(_yr_wdth.keys()):
                
                calendar.add_cell(make_bar(_yr_wdth[yr],
                                           border_color = colors[index % len(colors)],
                                           height = height, text = str(yr),
                                           styles = ["background: red",
                                                     "color: black"]))

        if disp_month:

            calendar = get_table()
            main_cal.add_row()
            main_cal.add_cell(calendar)
            for index, month in enumerate(month_width(start, end, width)):

                calendar.add_cell(make_bar(month[1],
                                           border_color =
                                           colors[index % len(colors)],
                                           height = height,
                                           text = str(month[0]),
                                           styles = ["background: red",
                                                     "color: black"]))

        if disp_day:
            calendar = get_table()
            main_cal.add_row()
            main_cal.add_cell(calendar)
            import math
            left = 0
            for index, day in enumerate([start + timedelta(days = day)
                                         for day in xrange(days)]):
                
                calendar.add_cell(make_bar(round(day_width + left),
                                           border_color = 
                                           colors[index % len(colors)],
                                           height = height,
                                           text = str(day.day),
                                           styles = ["background: red",
                                                     "color: black"]))
                left = day_width + left - round(day_width + left)
                
        return main_cal

    def get_table():
        calendar = Table()
        map(lambda nv:calendar.add_attr(nv[0], nv[1]),
            [("cellpadding","0"),
             ("cellspacing","0"),
             ("border","0")])
        return calendar


    def _get_gantt(project):
        try:
            return _get_gantt(project)
        except:
            return DivWdg(html = "Incomplete data for the project.", css = "height: 20px").get_display()
            
        
    def get_gantt(project):
    
        total_width = 1000.0
        first_col_wdth = 75.0
        tasks = all_tasks(project)
        start_date = pick_date_from_tasks(tasks)
        end_date = pick_date_from_tasks(tasks, field = "bid_end_date", func = max)
        days = (end_date - start_date).days
        # print "="*30, days
        pse = all_process_start_end(project, tasks)
        
        main = DivWdg()
        
        map(main.add_style, ("border-color: blue",
                             "border-style: solid",
                             "border-radius: 5px",
                             "border-width: 1px"))

        calendar = get_table()
        main.add(calendar)

        _empty = DivWdg()
        _empty.add_style("width: %fpx" %first_col_wdth)
        calendar.add_cell(_empty)
        calendar.add_cell(make_calendar(start_date, end_date, total_width, 20))
        # main.add("5")
        for process in pse.iteritems():
            # break
            if not process[0]: continue
            length = (process[1]["end"] - process[1]["start"])

            proc_div = DivWdg()
            # proc_div.add_style("float: right")
            map(proc_div.add_style, ("border-color: green",
                                     "height: 20px",
                                     "border-style: solid",
                                     "border-radius: 1px",
                                     "border-width: 1px"))

            text = DivWdg()
            map(text.add_style, ["color: black"])
            table = get_table()
            table.add_row()
            proc_div.add(table)
            # text.add_style("float: right")
            text.add_style("width: %fpx" %first_col_wdth)
            main.add(proc_div)
            text.add(str(process[0]) + ": ", index = 1)
            table.add_cell(text)
            # proc_div.add_style("float: right")

            table.add_cell(make_bar(((total_width *
                                          (process[1]["start"] -
                                           start_date).days)/days),
                                    border_width = 0, styles = []))
            
            
            table.add_cell(make_bar(((total_width/days * float(length.days))),
                                    border_color = "red", styles = ["background: green"]))
            
            main.add(proc_div)
            # proc_div.add()
        return main.get_display()

except:
    pass


from datetime import datetime, timedelta

def month_width(start, end, width):
    month_width = []
    days = (end - start).days
    step_size = (float(width)/days)
    for day in xrange(days):
        cur = start + timedelta(days = day)
        month = cur.strftime("%b")
        if month_width and month_width[-1][0] == month:
            month_width[-1][1] += step_size
        else:
            month_width.append([month, step_size])
    
    return month_width

def year_width(start, end, width):
    year_width = {}
    days = (end - start).days
    step_size = float(width)/days
    for day in xrange(days):
        cur = start + timedelta(days = day)
        year_width[cur.year] = step_size + year_width.get(cur.year, 0.0)
    print "total width: ", width
    print "sum of year widths: ", sum(year_width.values())
    return year_width

def pick_date_from_tasks(tasks, field = "bid_start_date", func = min):
    '''
    @tasks: is expected to be list of dictionaries representing individual tasks
    @field: key of the dictionary to be read for to be passed on to func.
            Both key and value should be string
    @func:  the function which will determine the max from an iterable
    '''

    return func(map(date_str_to_datetime,
                    [task[field] for task in tasks]))

def all_process_start_end(project, tasks = None):
    tasks = tasks if tasks else all_tasks(project)
    processes = all_task_processes(project, tasks = tasks)
    
    process_tasks = all_process_tasks(project, tasks = tasks)
    process_start_end = {}
    for process in processes:
        process_start_end[process] = {
            "start":
            pick_date_from_tasks(process_tasks[process])
                                 # .strftime("%Y-%m-%d %H:%M:%S")
            ,
            "end":
            pick_date_from_tasks(process_tasks[process],
                                 field = "bid_end_date",
                                 func = max)# .strftime("%Y-%m-%d %H:%M:%S")
        }
    return process_start_end

# print "projects: ", [proj["code"] for proj in all_projects()]
# print "all_task('vfx'): ", all_tasks('vfx', "animation")
# print "all_task_processes('vfx'): ", all_task_processes("vfx")
# print "all_process_tasks('vfx')['animation']: ", all_process_tasks('vfx', 'animation')
# print "pick_date_from_tasks(all_process_tasks('vfx', 'animation')): ", pick_date_from_tasks(all_process_tasks('vfx', 'animation'))
# print "all_process_start_end('vfx'): ", all_process_start_end('vfx')
