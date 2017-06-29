import math
import signal
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np
from interruptingcow import SignalWakeupHandler

import ModernGL


class QOpenGLControllerWidget(Q.QOpenGLWidget):
#    def __init__(self, *args, **kwargs):
#        super(QOpenGLControllerWidget,self).__init__(*args, **kwargs)

    def initializeGL(self):
        self.ctx = ctx = ModernGL.create_context()

    def paintGL(self):
        ctx = self.ctx
        ctx.viewport = (0, 0, self.width(), self.height())
        ctx.clear(0.9,0.9,0.9)
    def resizeGL(self, w, h):
        super().resizeGL(w,h)

def do_main(WidgetType):
    fmt = Q.QSurfaceFormat.defaultFormat()
    fmt.setVersion(4,5)
    fmt.setProfile(fmt.CoreProfile)
    Q.QSurfaceFormat.setDefaultFormat(fmt)
    Q.QCoreApplication.setAttribute(Q.Qt.AA_ShareOpenGLContexts)

    app = Q.QApplication([])
    with SignalWakeupHandler(app):
        signal.signal(signal.SIGINT, lambda *a: app.quit())
        win = Q.QMainWindow()
        wid = WidgetType(parent=win)
        win.setCentralWidget(wid)
        win.move(Q.QDesktopWidget().rect().center() - win.rect().center())
        win.show()

        sys.exit(app.exec_())
