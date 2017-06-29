from common import *
import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL
from PyQt5 import QtCore, QtOpenGL, QtWidgets


class AlphaBlendingWidget(QOpenGLControllerWidget):
    def __init__(self, *args, **kwargs):
        super(AlphaBlendingWidget,self).__init__(*args, **kwargs)
        self.timer = Q.QElapsedTimer()

    def initializeGL(self):
        super().initializeGL()
        prog = self.ctx.program([
            self.ctx.vertex_shader('''
                #version 330

                in vec2 vert;

                in vec4 vert_color;
                out vec4 frag_color;

                uniform vec2 scale;
                uniform float rotation;

                void main() {
                    frag_color = vert_color;
                    float r = rotation * (0.5 + gl_InstanceID * 0.05);
                    mat2 rot = mat2(cos(r), sin(r), -sin(r), cos(r));
                    gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
                }
            '''),
            self.ctx.fragment_shader('''
                #version 330

                in vec4 frag_color;
                out vec4 color;

                void main() {
                    color = vec4(frag_color);
                }
            '''),
        ])

        self.scale = prog.uniforms['scale']
        self.rotation = prog.uniforms['rotation']

        vbo = self.ctx.buffer(struct.pack(
            '18f',
            1.0, 0.0, 1.0, 0.0, 0.0, 0.5,
            -0.5, 0.86, 0.0, 1.0, 0.0, 0.5,
            -0.5, -0.86, 0.0, 0.0, 1.0, 0.5,
        ))

        self.vao = self.ctx.simple_vertex_array(prog, vbo, ['vert', 'vert_color'])

        self.timer.restart()

    def paintGL(self):
        super().paintGL()
        self.scale.value = (self.height() / self.width() * 0.75, 0.75)
        self.rotation.value = self.timer.elapsed() / 1000
        self.ctx.enable(ModernGL.BLEND)
        self.vao.render(instances=10)
        self.ctx.finish()
        self.update()

do_main( AlphaBlendingWidget)
