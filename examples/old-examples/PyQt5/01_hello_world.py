from common import *
import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL
from PyQt5 import QtOpenGL, QtWidgets

class HelloWorldWidget(QOpenGLControllerWidget):
    def initializeGL(self):
        super().initializeGL()
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
                    color = vec4(0.30, 0.50, 1.00, 1.0);
                }
            '''),
        ])

        vbo = self.ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
        self.vao = self.ctx.simple_vertex_array(prog, vbo, ['vert'])

    def paintGL(self):
        super().paintGL()
        self.vao.render()
        self.ctx.finish()


do_main( HelloWorldWidget)
