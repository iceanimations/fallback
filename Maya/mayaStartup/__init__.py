import src._startup as startup
import src.jobs as jobs
reload(jobs)
reload(startup)

FPSDialog = jobs.FPSDialog


def start():
    startup.addScriptJobs()