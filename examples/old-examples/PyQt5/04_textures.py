import os

import ModernGL
from PIL import Image
from common import *
import math
import struct
import random
import sys
import PyQt5.Qt as Q, PyQt5.QtCore, PyQt5.QtGui, PyQt5.QtWidgets
import numpy as np

class TexturesWidget(QOpenGLControllerWidget):
    def __init__(self, *args, **kwargs):
        super(TexturesWidget,self).__init__(*args, **kwargs)
        self.timer = Q.QElapsedTimer()
        self.timer.restart()

    def initializeGL(self):
        super().initializeGL()
        img = Image.open(os.path.join(os.path.dirname(__file__), '..', 'data', 'noise.jpg'))
        texture = self.ctx.texture(img.size, 3, img.tobytes())
        texture.use()

        prog = self.ctx.program([
            self.ctx.vertex_shader('''
                #version 330

                in vec2 vert;
                in vec2 tex_coord;
                out vec2 v_tex_coord;

                uniform vec2 scale;
                uniform float rotation;

                void main() {
                    mat2 rot = mat2(
                        cos(rotation), sin(rotation),
                        -sin(rotation), cos(rotation)
                    );
                    gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
                    v_tex_coord = tex_coord;
                }
            '''),
            self.ctx.fragment_shader('''
                #version 330

                uniform sampler2D texture;

                in vec2 v_tex_coord;
                out vec4 color;

                void main() {
                    color = vec4(texture2D(texture, v_tex_coord).rgb, 1.0);
                }
            '''),
        ])

        self.scale = prog.uniforms['scale']
        self.rotation = prog.uniforms['rotation']

        vbo = self.ctx.buffer(struct.pack(
            '12f',
            1.0, 0.0, 0.5, 1.0,
            -0.5, 0.86, 1.0, 0.0,
            -0.5, -0.86, 0.0, 0.0,
        ))

        self.vao = self.ctx.simple_vertex_array(prog, vbo, ['vert', 'tex_coord'])

    def paintGL(self):
        super().paintGL()
        self.scale.value = (self.height() / self.width() * 0.75, 0.75)
        self.rotation.value = self.timer.elapsed() / 1000
        self.vao.render()
        self.ctx.finish()
        self.update()

do_main( TexturesWidget)
