import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL


class QOpenGLControllerWidget(Q.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        fmt = Q.QSurfaceFormat()
        fmt.setVersion(4,5)
        fmt.setProfile(fmt.CoreProfile)
        fmt.setOption(fmt.DebugContext)
        super(QOpenGLControllerWidget,self).__init__(*args, **kwargs)

    def initializeGL(self):
        self.ctx = ModernGL.create_context()

        prog = self.ctx.program([
            self.ctx.vertex_shader('''
                #version 330
                in vec2 vert;
                void main() {
                    gl_Position = vec4(vert, 0.0, 1.0);
                }
            '''),
            self.ctx.fragment_shader('''
                #version 330
                out vec4 color;
                void main() {
                    color = vec4(0.3, 0.5, 1.0, 1.0);
                }
            '''),
        ])

        vbo = self.ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
        self.vao = self.ctx.simple_vertex_array(prog, vbo, ['vert'])

    def paintGL(self):
        self.ctx.viewport = (0, 0, self.width(), self.height())
        self.ctx.clear(0.9, 0.9, 0.9)
        self.vao.render()
        self.ctx.finish()

    def resizeGL(self,w,h):
        super().resizeGL(w,h)

fmt = Q.QSurfaceFormat.defaultFormat()
fmt.setVersion(4,5)
fmt.setProfile(fmt.CoreProfile)
fmt.setOption(fmt.DebugContext)
Q.QSurfaceFormat.setDefaultFormat(fmt)
del fmt
Q.QCoreApplication.setAttribute(Q.Qt.AA_ShareOpenGLContexts)

app = Q.QApplication([])

win = Q.QMainWindow()
wid = QOpenGLControllerWidget(parent=win)
win.setCentralWidget(wid)
win.move(Q.QDesktopWidget().rect().center() - win.rect().center())
win.show()

sys.exit(app.exec_())

