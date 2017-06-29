from common import *
import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

import ModernGL


class Texture3DWidget(QOpenGLControllerWidget):
    def initializeGL(self):
        super().initializeGL()
        ctx = self.ctx
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
        super().paintGL()
        self.vao.render(ModernGL.TRIANGLE_STRIP)

do_main( Texture3DWidget )
