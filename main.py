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
from kivy.resources import resource_find

import math

# ===== КОНСТАНТЫ =====
CIRCLE_RADIUS_RATIO = 0.25  # 0.35 > x > 0.05

COLOR_TOP = (1, 1, 0)     # жёлтый
COLOR_BOTTOM = (0, 0, 1)  # синий
BG_COLOR = (0, 0, 0)


class TwoCirclesWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.offset = None
        self.start_touch_y = None
        self.start_offset = None

        with self.canvas:
            Color(*BG_COLOR)
            self.bg = Rectangle()

            Color(*COLOR_TOP)
            self.circle_top = Ellipse()

            Color(*COLOR_BOTTOM)
            self.circle_bottom = Ellipse()

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

        # фон
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

    # ===== ЖЕСТ ОДНИМ ПАЛЬЦЕМ =====

    def on_touch_down(self, touch):
        self.start_touch_y = touch.y
        self.start_offset = self.offset
        return True

    def on_touch_move(self, touch):
        if self.start_touch_y is None:
            return

        dy = touch.y - self.start_touch_y
        self.offset = self.start_offset + dy
        self.update()

    def on_touch_up(self, touch):
        self.start_touch_y = None
        self.start_offset = None


class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.circles = TwoCirclesWidget()
        self.add_widget(self.circles)

        btn_menu = Button(
            text="Menu",
            size_hint=(None, None),
            size=(dp(120), dp(56)),
            pos_hint={"x": 0, "top": 1}
        )
        btn_menu.bind(on_release=self.open_menu)
        self.add_widget(btn_menu)

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
            size=(dp(300), dp(200))
        )
        self.menu_popup.open()

    def close_popup(self, *args):
        if hasattr(self, "menu_popup"):
            self.menu_popup.dismiss()

    def show_about(self, *args):
        if hasattr(self, "menu_popup"):
            self.menu_popup.dismiss()

        path = resource_find("about.txt")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = "About file not found"

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
