import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
site.addsitedir(r"r:/Python_Scripts")
import src._window as window
reload(window)
import sys
app = False
try:
    import PySide
except:
    from PyQt4.QtGui import QApplication
    app = True

def run():
    global app
    if app:
        app = QApplication(sys.argv)
    global win
    win = window.Window()
    win.show()
    if app:
        sys.exit(app.exec_())

if __name__ == "__main__":
    run()