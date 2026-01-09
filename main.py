from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
import math

# ===== КОНСТАНТЫ =====
CIRCLE_RADIUS_RATIO = 0.25  # (0.20)   0.35  >x>  0.05

COLOR_TOP = (1, 1, 0)
COLOR_BOTTOM = (0, 0, 1)
BG_COLOR = (0, 0, 0)


def add_colors(c1, c2):
    return (
        min(c1[0] + c2[0], 1.0),
        min(c1[1] + c2[1], 1.0),
        min(c1[2] + c2[2], 1.0),
    )


class TwoCirclesWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.touches = {}
        self.offset = None

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

        if self.offset is None:
            self.offset = h / 4

        self.offset = max(0, min(self.offset, h / 2))

        top_center = (cx, cy + self.offset)
        bottom_center = (cx, cy - self.offset)

        self.bg.pos = self.pos
        self.bg.size = self.size

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

        dist = math.dist(top_center, bottom_center)

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


class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.circles = TwoCirclesWidget()
        self.add_widget(self.circles)

        # кнопка Menu
        btn_menu = Button(
            text="Menu",
            size_hint=(None, None),
            size=(dp(120), dp(56)),
            pos_hint={"x": 0, "top": 1}
        )
        btn_menu.bind(on_release=self.open_menu)
        self.add_widget(btn_menu)

        # кнопка Exit
        btn_exit = Button(
            text="Exit",
            size_hint=(None, None),
            size=(dp(120), dp(56)),
            pos_hint={"right": 1, "top": 1}
        )
        btn_exit.bind(on_release=self.exit_app)
        self.add_widget(btn_exit)

    def open_menu(self, *args):
        
        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12)
        )        
        
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        btn_settings = Button(
            text="Settings",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(16)
        )        
        btn_settings.bind(on_release=self.close_popup)

        btn_about = Button(
            text="About",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(16)
        )
        btn_about.bind(on_release=self.show_about)

        layout.add_widget(btn_settings)
        layout.add_widget(btn_about)

        self.menu_popup = Popup(
            title="Menu",
            content=layout,
            size_hint=(None, None),
            size=(300, 200)
        )
        self.menu_popup.open()

    def close_popup(self, *args):
        if hasattr(self, "menu_popup"):
            self.menu_popup.dismiss()

    def show_about(self, *args):
        if hasattr(self, "menu_popup"):
            self.menu_popup.dismiss()

        text = (
            "Impossible Colors\n\n"
            "Author: caveeagle\n"
        )

        label = Label(
            text=text,
            halign="center",
            valign="middle",
            text_size=(dp(360), None)
        )
    
        label.bind(
            texture_size=lambda inst, size: setattr(inst, "height", size[1])
        )
    
        popup = Popup(
            title="About",
            content=label,
            size_hint=(None, None),
            size=(dp(420), dp(300))
        )
    
        popup.open()

    def exit_app(self, *args):
        App.get_running_app().stop()


class MyApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return MainLayout()


MyApp().run()
