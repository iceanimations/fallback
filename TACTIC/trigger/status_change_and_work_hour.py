#pre-generated########################################################
# from pyasm.common import jsondumps, jsonloads
# tsobj = input.get('trigger_sobject')
# task = input.get('update_data')
# task_status = task.get('status')
# data = tsobj.get('data')
# data = jsonloads(data)
# src_status = data.get("src_status")
# if task_status != src_status:
#     pass
###################### Add the script below: ############################
from pyasm.common import Environment, TacticException
import sys, os
def user_tasks(user = "", status = ""):    
    search_type = "sthpw/task"
    filter = []
    filter.append(("assigned", "%s" %(LOGIN if not user else user)))
    if status:
        filter.append(("status", "%s" %(status)))
    
    return server.query(search_type, filter, return_sobjects=True)
        
def day():
    from datetime import date, timedelta
    from datetime import datetime
    d = date.today()
    return (datetime.combine(d, datetime.min.time()) +
            timedelta(hours = 5))

def now():
    from datetime import date, timedelta
    from datetime import datetime
    return datetime.now() + timedelta(hours = 5)

def calcTime(start, end):
    
    from datetime import datetime
    start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    duration = (end - start)
    return durationInHours(duration)


def durationInHours(duration):
    
    dur = 0
    
    if duration.days > 0:
        dur += duration.days * 8
    
    hours = duration.seconds/3600
    
    if hours > 8:
        dur += hours

    return dur if dur > 1 else 1

    
def addWorkHour(task):
    search_type = "sthpw/work_hour"
    print "addWorkHour"
    print task
    data = {"category": "regular",
            "day": str(day()),
            "straight_time": -1 if "done" not in task.get("status").lower() else 0,
            "start_time": str(now()),
            "search_type": task.get("search_type"),
            "task_code": task.get("code"),
            "process": task.get("process"),
            "status": task.get("status")}
    server.insert(search_type, data# , parent_key = task.get_search_key()
    )

class FileType():
    def write(self, content):

        with open(r"C:/ProgramData/Southpaw/Tactic/print.log", "a") as p:
            p.write(content)
sys.stdout = sys.stderr = FileType()
def main(serv, inp):
    print "Main called" + "="*50
    global server
    global input
    global LOGIN
    global QUEUE
    print input
    
    server = serv
    input = inp
    LOGIN = server.eval("$LOGIN")
    QUEUE = "Queued"
    update_data = input.get("update_data")
    search_key = input.get("search_key")
    TASK = server.get_by_search_key(search_key)
    if ("progress" not in TASK.get("status").lower() and
        "progress" in input.get("prev_data")["status"].lower()):
        
        for work_hour in  server.query("sthpw/work_hour",
                                       [("task_code", TASK.get("code")),
                                        ("straight_time", -1)],
                                       return_sobjects = True):
            if "progress" in work_hour.get("status").lower():
                server.update(work_hour.get_search_key(),
                              {"straight_time":
                               calcTime(work_hour.get("start_time"), now()),
                               "end_time": str(now())})
        return
        
    # iterate all the users' tasks
    for task in user_tasks(TASK["assigned"]):
        
        task_sk = task.get_search_key()

        work_hours = server.query("sthpw/work_hour",
                                  [("task_code", task.get("code"))],
                                  return_sobjects = True)

        # # iterate all the work hours associated with that task
        # for work_hour in work_hours:

        #     # close done all work hours which have straight hours == -1
        #     if work_hour.get("straight_time") == -1:
        #         server.update(work_hour.get_search_key(),
        #                       {"straight_time":
        #                        calcTime(work_hour.get("start_time"), now()),
        #                        "end_time": str(now())})

        if ((task_sk != search_key) and # skip the current task
            ("progress" in TASK.get("status").lower()) and
            # skip the approved and/or done tasks
            ("progress" in task.get("status").lower())):

            server.update(task_sk, {"status": QUEUE})
            
    addWorkHour(TASK)
