from common import *
import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL
from PyQt5 import QtCore, QtOpenGL, QtWidgets


class UniformAndAttributeWidget(QOpenGLControllerWidget):
    def __init__(self, *args, **kwargs):
        super(UniformAndAttributeWidget,self).__init__(*args, **kwargs)
        self.timer = Q.QElapsedTimer()
        self.timer.restart()

    def initializeGL(self):
        super().initializeGL()
        prog = self.ctx.program([
            self.ctx.vertex_shader('''
                #version 330

                in vec2 vert;

                in vec3 vert_color;
                out vec3 frag_color;

                uniform vec2 scale;
                uniform float rotation;

                void main() {
                    frag_color = vert_color;
                    mat2 rot = mat2(
                        cos(rotation), sin(rotation),
                        -sin(rotation), cos(rotation)
                    );
                    gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
                }
            '''),
            self.ctx.fragment_shader('''
                #version 330

                in vec3 frag_color;
                out vec4 color;

                void main() {
                    color = vec4(frag_color, 1.0);
                }
            '''),
        ])

        self.scale = prog.uniforms['scale']
        self.rotation = prog.uniforms['rotation']

        vbo = self.ctx.buffer(struct.pack(
            '15f',
            1.0, 0.0, 1.0, 0.0, 0.0,
            -0.5, 0.86, 0.0, 1.0, 0.0,
            -0.5, -0.86, 0.0, 0.0, 1.0,
        ))

        self.vao = self.ctx.simple_vertex_array(prog, vbo, ['vert', 'vert_color'])

    def paintGL(self):
        super().paintGL()
        self.scale.value = (self.height() / self.width() * 0.75, 0.75)
        self.rotation.value = self.timer.elapsed() / 1000
        self.vao.render()
        self.ctx.finish()
        self.update()


do_main( UniformAndAttributeWidget)

