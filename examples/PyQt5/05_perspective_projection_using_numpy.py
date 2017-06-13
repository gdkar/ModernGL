import math
import struct
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL


def perspective(fov, ratio, near, far):
    zmul = (-2.0 * near * far) / (far - near)
    ymul = 1.0 / math.tan(fov * math.pi / 360.0)
    xmul = ymul / ratio
    return np.matrix([
        [xmul, 0.0, 0.0, 0.0],
        [0.0, ymul, 0.0, 0.0],
        [0.0, 0.0, -1.0, zmul],
        [0.0, 0.0, -1.0, 0.0],
    ])


def lookat(eye, target, up):
    forward = target - eye
    forward /= np.linalg.norm(forward)
    side = np.cross(forward, up)
    side /= np.linalg.norm(side)
    upward = np.cross(side, forward)
    upward /= np.linalg.norm(upward)

    return np.matrix([
        [side[0], side[1], side[2], -np.dot(eye, side)],
        [upward[0], upward[1], upward[2], -np.dot(eye, upward)],
        [-forward[0], -forward[1], -forward[2], np.dot(eye, forward)],
        [0.0, 0.0, 0.0, 1.0],
    ])


def create_mvp(proj, view):
    return np.transpose(proj @ view).astype(np.float32)


class QOpenGLControllerWidget(Q.QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        fmt = Q.QSurfaceFormat()
        fmt.setVersion(4,5)
        fmt.setProfile(fmt.CoreProfile)
        fmt.setOption(fmt.DebugContext)
        super(QOpenGLControllerWidget,self).__init__(*args, **kwargs)
        self.setFormat(fmt)

    def initializeGL(self):
        self.ctx = ctx = ModernGL.create_context()
        prog = ctx.program([
            ctx.vertex_shader('''
                #version 330

                uniform mat4 Mvp;

                in vec3 in_vert;

                void main() {
                    gl_Position = Mvp * vec4(in_vert, 1.0);
                }
            '''),
            ctx.fragment_shader('''
                #version 330

                out vec4 f_color;

                void main() {
                    f_color = vec4(0.0, 0.0, 0.0, 1.0);
                }
            ''')
        ])
        mvp = prog.uniforms['Mvp']
        self.mvp = mvp
        grid = bytes()
        for i in range(0, 65):
            grid += struct.pack('6f', i - 32, -32.0, 0.0, i - 32, 32.0, 0.0)
            grid += struct.pack('6f', -32.0, i - 32, 0.0, 32.0, i - 32, 0.0)

        vbo = ctx.buffer(grid)
        self.vao = ctx.simple_vertex_array(prog, vbo, ['in_vert'])

    def paintGL(self):
        self.ctx.viewport = ( 0, 0, self.width(),self.height())
        self.ctx.clear(0.9,0.9,0.9)
        proj = perspective(45.0, self.width() / self.height(), 0.1, 1000.0)
        view = lookat(
            np.array([80.0, 70.0, 60.0]),
            np.array([0.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        )
        self.mvp.write(create_mvp(proj, view))
        self.vao.render(ModernGL.LINES, 65 * 4)
    def resizeGL(self, w, h):
        super().resizeGL(w, h)

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
