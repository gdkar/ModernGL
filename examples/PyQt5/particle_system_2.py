from common import *
import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL

# Window & Context

class ParticleSystem2Widget(QOpenGLControllerWidget):
    def __init__(self, *args, **kwargs):
        super(ParticleSystem2Widget,self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.timer = Q.QTimer()
        self.timer.setInterval(1000/60)
        self.timer.setTimerType(Q.Qt.PreciseTimer)
        self.timer.timeout.connect(self.update)
        self.timer.start()
        self._mouse_pos = ( 0, 0)

    def particle(self):
        a = random.uniform(0.0, math.pi * 2.0)
        r = random.uniform(0.0, 1.0)
        cx, cy = self._mouse_pos[0], self.height()-self._mouse_pos[1]
        return struct.pack('2f2f', cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r)

    def initializeGL(self):
        super().initializeGL()
        ctx = self.ctx
        self.prog = prog = ctx.program([
            ctx.vertex_shader('''
                #version 330

                uniform vec2 Screen;
                in vec2 vert;

                void main() {
                    gl_Position = vec4((vert / Screen) * 2.0 - 1.0, 0.0, 1.0);
                }
            '''),
            ctx.fragment_shader('''
                #version 330

                out vec4 color;

                void main() {
                    color = vec4(0.30, 0.50, 1.00, 1.0);
                }
            ''')
        ])

        tvert = ctx.vertex_shader('''
            #version 330

            in vec2 in_pos;
            in vec2 in_prev;

            out vec2 out_pos;
            out vec2 out_prev;

            void main() {
                out_pos = in_pos * 2.0 - in_prev;
                out_prev = in_pos;
            }
        ''')

        transform = ctx.program(tvert, ['out_pos', 'out_prev'])

        self.vbo1 = vbo1 = ctx.buffer(b''.join(self.particle() for i in range(1024)))
        self.vbo2 = vbo2 = ctx.buffer(reserve=vbo1.size)

        self.vao1 = ctx.simple_vertex_array(transform, vbo1, ['in_pos', 'in_prev'])
        self.vao2 = ctx.simple_vertex_array(transform, vbo2, ['in_pos', 'in_prev'])

        self.render_vao = ctx.vertex_array(prog, [
            (vbo1, '2f8x', ['vert']),
        ])
#        transform.uniforms['acc'].value = (0, -0.0001)
        ctx.point_size = 5.0
        self.idx = 0

    def paintGL(self):
        ctx = self.ctx
        ctx.viewport = (0,0,self.width(),self.height())
        ctx.clear(0.9, 0.9, 0.9)
        self.prog.uniforms['Screen'].value = (self.width(),self.height())
        for i in range(8):
            self.vbo1.write(self.particle(), offset=self.idx * struct.calcsize('2f2f'))
            self.idx = (self.idx + 1) % 1024

        self.render_vao.render(ModernGL.POINTS, 1024)
        self.vao1.transform(self.vbo2, ModernGL.POINTS, 1024)
        ctx.copy_buffer(self.vbo1, self.vbo2)

    def mouseMoveEvent(self, evt):
        self._mouse_pos = (evt.pos().x(),evt.pos().y())
        evt.ignore()
#        super().mouseMoveEvent(evt)


do_main( ParticleSystem2Widget )
