import site
site.addsitedir(r"\\ICE-088\site-packages")

try:
    plugins.matte_works.matteWorker.matteWork()
except:
    import plugins.matte_works