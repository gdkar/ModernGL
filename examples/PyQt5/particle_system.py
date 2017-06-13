import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL

# Window & Context

class QOpenGLControllerWidget(Q.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        fmt = Q.QSurfaceFormat()
        fmt.setVersion(4,5)
        fmt.setProfile(fmt.CoreProfile)
        fmt.setOption(fmt.DebugContext)
        super(QOpenGLControllerWidget,self).__init__(*args, **kwargs)
        self.setFormat(fmt)
        self.timer = Q.QTimer()
        self.timer.setInterval(1000/60)
        self.timer.setTimerType(Q.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update)
        self.timer.start()
    def particle(self):
        a = random.uniform(0.0, math.pi * 2.0)
        r = random.uniform(0.0, 0.001)

        return struct.pack('2f2f', 0.0, 0.0, math.cos(a) * r - 0.003, math.sin(a) * r - 0.008)

    def initializeGL(self):
        self.ctx = ctx = ModernGL.create_context()
        tvert = ctx.vertex_shader('''
            #version 330

            uniform vec2 acc;

            in vec2 in_pos;
            in vec2 in_prev;

            out vec2 out_pos;
            out vec2 out_prev;

            void main() {
                out_pos = in_pos * 2.0 - in_prev + acc;
                out_prev = in_pos;
            }
        ''')

        vert = ctx.vertex_shader('''
            #version 330

            in vec2 vert;

            void main() {
                gl_Position = vec4(vert, 0.0, 1.0);
            }
        ''')

        frag = ctx.fragment_shader('''
            #version 330

            out vec4 color;

            void main() {
                color = vec4(0.30, 0.50, 1.00, 1.0);
            }
        ''')

        self.prog = prog = ctx.program([vert, frag])

        self.transform = transform = ctx.program(tvert, ['out_pos', 'out_prev'])

        self.vbo1 = vbo1 = ctx.buffer(b''.join(self.particle() for i in range(65536)))
        self.vbo2 = vbo2 = ctx.buffer(reserve=vbo1.size)

        self.vao1 = ctx.simple_vertex_array(transform, vbo1, ['in_pos', 'in_prev'])
        self.vao2 = ctx.simple_vertex_array(transform, vbo2, ['in_pos', 'in_prev'])

        self.render_vao = ctx.vertex_array(prog, [
            (vbo1, '2f8x', ['vert']),
        ])
        transform.uniforms['acc'].value = (0, -0.0001)
        ctx.point_size = 5.0
        self.idx = 0

    def paintGL(self):
        ctx = self.ctx
        ctx.viewport = (0,0,self.width(),self.height())
        ctx.clear(0.9, 0.9, 0.9)
        for i in range(64):
            self.vbo1.write(self.particle(), offset=self.idx * struct.calcsize('2f2f'))
            self.idx = (self.idx + 1) % 65536

        self.render_vao.render(ModernGL.POINTS, 65526)
        self.vao1.transform(self.vbo2, ModernGL.POINTS, 65536)
        ctx.copy_buffer(self.vbo1, self.vbo2)
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
