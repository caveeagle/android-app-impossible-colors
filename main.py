from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
import math

# ===== КОНСТАНТЫ =====
CIRCLE_RADIUS_RATIO = 0.05   # относительный радиус от ширины экрана

COLOR_TOP = (1, 0, 0)        # красный
COLOR_BOTTOM = (0, 0, 1)     # синий
BG_COLOR = (0, 0, 0)         # чёрный


def add_colors(c1, c2):
    """Покомпонентное сложение RGB с ограничением"""
    return (
        min(c1[0] + c2[0], 1.0),
        min(c1[1] + c2[1], 1.0),
        min(c1[2] + c2[2], 1.0),
    )


class TwoCirclesWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.touches = {}
        self.offset = None  # будет инициализирован после получения размеров

        with self.canvas:
            Color(*BG_COLOR)
            self.bg = Rectangle()

            Color(*COLOR_TOP)
            self.circle_top = Ellipse()

            Color(*COLOR_BOTTOM)
            self.circle_bottom = Ellipse()

            self.intersection_color = Color(0, 0, 0, 0)
            self.circle_intersection = Ellipse()

        self.bind(size=self.update, pos=self.update)

    def update(self, *args):
        w, h = self.size
        cx, cy = w / 2, h / 2

        radius = CIRCLE_RADIUS_RATIO * w

        # начальное положение:
        # расстояние между центрами = половина высоты экрана
        if self.offset is None:
            self.offset = h / 4

        # ограничение смещения
        self.offset = max(0, min(self.offset, h / 2))

        top_center = (cx, cy + self.offset)
        bottom_center = (cx, cy - self.offset)

        # фон
        self.bg.pos = self.pos
        self.bg.size = self.size

        # основные круги
        size = (radius * 2, radius * 2)
        self.circle_top.size = size
        self.circle_bottom.size = size

        self.circle_top.pos = (
            top_center[0] - radius,
            top_center[1] - radius
        )
        self.circle_bottom.pos = (
            bottom_center[0] - radius,
            bottom_center[1] - radius
        )

        # расстояние между центрами
        dist = math.dist(top_center, bottom_center)

        # ===== ПЕРЕСЕЧЕНИЕ =====
        if dist < 2 * radius:
            overlap_radius = (2 * radius - dist) / 2
            overlap_center_y = (top_center[1] + bottom_center[1]) / 2

            self.circle_intersection.size = (
                overlap_radius * 2,
                overlap_radius * 2
            )
            self.circle_intersection.pos = (
                cx - overlap_radius,
                overlap_center_y - overlap_radius
            )

            r, g, b = add_colors(COLOR_TOP, COLOR_BOTTOM)
            self.intersection_color.rgba = (r, g, b, 1)

        else:
            self.intersection_color.rgba = (0, 0, 0, 0)

    # ===== ОБРАБОТКА ЖЕСТА =====

    def on_touch_down(self, touch):
        self.touches[touch.id] = touch.pos

    def on_touch_move(self, touch):
        if touch.id in self.touches:
            self.touches[touch.id] = touch.pos

        if len(self.touches) == 2:
            p1, p2 = self.touches.values()
            self.offset = math.dist(p1, p2) / 2
            self.update()

    def on_touch_up(self, touch):
        self.touches.pop(touch.id, None)


class MyApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return TwoCirclesWidget()


MyApp().run()
