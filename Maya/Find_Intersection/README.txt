To easily run this code add the python code at the bottom of this document to your shelf. And ensure that this package is in MAYA_DIRECTORY\python\site-packages\plugins\

import site

site.addsitedir("\\ICE-088\site-packages")
try:
    plugins.Find_Intersection.IntFinder.intFind()
except:
    import plugins.Find_Intersection