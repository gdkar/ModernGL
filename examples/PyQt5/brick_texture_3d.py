import math
from math import sin, cos
import struct
import random
from random import randrange
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL
from pyrr import Matrix44

def create_brick_texture(size):
    result = bytearray()

    for z in range(size[2]):
        for y in range(size[1]):
            for x in range(size[0]):

                if x != size[0] - 1 and y != size[1] - 1 and z != size[2] - 1:
                    n1, n2, n3 = randrange(0, 16), randrange(0, 16), randrange(0, 16)
                    result += struct.pack('BBB', 220 + n1, 31 + n2, 0 + n3)

                else:
                    n = randrange(0, 16)
                    result += struct.pack('BBB', 240 - n, 240 - n, 240 - n)

    return bytes(result)



class QOpenGLControllerWidget(Q.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        fmt = Q.QSurfaceFormat()
        fmt.setVersion(4,5)
        fmt.setProfile(fmt.CoreProfile)
        fmt.setOption(fmt.DebugContext)
        super(QOpenGLControllerWidget,self).__init__(*args, **kwargs)
        self._retimer = Q.QTimer()
        self._retimer.setTimerType(Q.Qt.PreciseTimer)
        self._retimer.setInterval(1000//60)
        self._retimer.timeout.connect(self.update)
        self._retimer.start()
        self._timer = Q.QElapsedTimer()
        self._timer.start()

    def initializeGL(self):
        self.ctx = ctx = ModernGL.create_context()
        prog = ctx.program([
            ctx.vertex_shader('''
                #version 330

                uniform mat4 Mvp;
                uniform vec3 TextureSize;

                in vec3 vert;
                out vec3 v_text;

                void main() {
                    v_text = vert * 100.0 / TextureSize;
                    gl_Position = Mvp * vec4(vert, 1.0);
                }
            '''),
            ctx.fragment_shader('''
                #version 330

                uniform sampler3D Texture;

                in vec3 v_text;
                out vec4 color;

                void main() {
                    color = texture(Texture, v_text);
                }
            '''),
        ])

        self.mvp = mvp = prog.uniforms['Mvp']
        self.texture_size = texture_size = prog.uniforms['TextureSize']

        vbo = ctx.buffer(struct.pack(
            '36f',

            0.0, 0.0, 0.0,
            2.0, 0.0, 0.0,
            0.0, 2.0, 0.0,

            0.0, 0.0, 0.0,
            2.0, 0.0, 0.0,
            0.0, 0.0, 2.0,

            0.0, 0.0, 0.0,
            0.0, 2.0, 0.0,
            0.0, 0.0, 2.0,

            2.0, 0.0, 0.0,
            0.0, 2.0, 0.0,
            0.0, 0.0, 2.0,
        ))

        self.vao = vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

        size = (20, 16, 8)
        texture_size.value = size
        self.texture = texture = ctx.texture3d(size, 3, create_brick_texture(size))
        texture.filter = ModernGL.NEAREST
        texture.use()

        ctx.enable(ModernGL.DEPTH_TEST)

    def paintGL(self):
        ctx = self.ctx
        angle = self._timer.nsecsElapsed() * 1e-9
        width, height = self.width(),self.height()
        proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (cos(angle) * 5.0, sin(angle) * 5.0, 2.5),
            (0.0, 0.0, 0.5),
            (0.0, 0.0, 1.0),
        )

        self.mvp.write((proj * lookat).astype('float32').tobytes())

        ctx.viewport = ( 0, 0, self.width(), self.height())
        ctx.clear(0.9, 0.9, 0.9)
        self.vao.render()

fmt = Q.QSurfaceFormat.defaultFormat()
fmt.setVersion(4,5)
fmt.setProfile(fmt.CoreProfile)
fmt.setOption(fmt.DebugContext)
Q.QSurfaceFormat.setDefaultFormat(fmt)
Q.QCoreApplication.setAttribute(Q.Qt.AA_ShareOpenGLContexts)

app = Q.QApplication([])

win = Q.QMainWindow()
wid = QOpenGLControllerWidget(parent=win)
win.setCentralWidget(wid)
win.move(Q.QDesktopWidget().rect().center() - win.rect().center())
win.show()

sys.exit(app.exec_())
