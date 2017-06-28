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
        self.ctx = ctx = ModernGL.create_context()
        prog = ctx.program([
            ctx.vertex_shader('''
                #version 450

                in vec2 vert;
                in vec3 tex_coord;
                out vec3 v_tex_coord;

                void main() {
                    gl_Position = vec4(vert, 0.0, 1.0);
                    v_tex_coord = tex_coord;
                }
            '''),
            ctx.fragment_shader('''
                #version 450

                uniform sampler3D Texture;

                in vec3 v_tex_coord;
                out vec4 color;

                void main() {
                    color = vec4(texture(Texture, v_tex_coord).rgb, 1.0);
                }
            '''),
        ])

        data = bytes()

        for i in range(11):
            data += struct.pack('5f', i / 10.0 - 0.5, 0.2, random.random(), random.random(), random.random())
            data += struct.pack('5f', i / 10.0 - 0.5, -0.2, random.random(), random.random(), random.random())

        self.vbo = vbo = ctx.buffer(data)

        self.vao = vao = ctx.simple_vertex_array(prog, vbo, ['vert', 'tex_coord'])

        self.pixels = pixels = bytes()

        for i in range(4):
            for j in range(4):
                for k in range(4):
                    r = int(i * 255 / 3)
                    g = int(j * 255 / 3)
                    b = int(k * 255 / 3)
                    pixels += struct.pack('3B', r, g, b)

        self.texture = texture = ctx.texture3d((4, 4, 4), 3, pixels)
        texture.use()

    def paintGL(self):
        ctx = self.ctx
        ctx.viewport = (0, 0, self.width(), self.height())
        ctx.clear(0.9, 0.9, 0.9)
        self.vao.render(ModernGL.TRIANGLE_STRIP)

    def resizeGL(self,w,h):
        super().resizeGL(w,h)

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
