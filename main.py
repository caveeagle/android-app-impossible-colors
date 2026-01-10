from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.resources import resource_find
from kivy.config import ConfigParser

import os
import math

# ===== КОНСТАНТЫ =====
CIRCLE_RADIUS_RATIO = 0.25
BG_COLOR = (0, 0, 0)


# ==================== TWO CIRCLES ====================

class TwoCirclesWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.offset = None
        self.start_touch_y = None
        self.start_offset = None

        self.color_scheme = "yb"  # yb | rg

        with self.canvas:
            Color(*BG_COLOR)
            self.bg = Rectangle()

            self.color_top_instr = Color(1, 1, 0)   # yellow
            self.circle_top = Ellipse()

            self.color_bottom_instr = Color(0, 0, 1)  # blue
            self.circle_bottom = Ellipse()

        self.bind(size=self.update, pos=self.update)

        self.load_state()

    # ---------- STATE ----------

    def load_state(self):
        app = App.get_running_app()

        scheme = app.config.get("color", "scheme")
        self.set_color_scheme(scheme)

        saved_offset = float(app.config.get("circles", "offset"))
        if saved_offset > 0:
            self.offset = saved_offset

    def save_offset(self):
        app = App.get_running_app()
        app.config.set("circles", "offset", str(self.offset))
        app.config.write()

    # ---------- COLORS ----------

    def set_color_scheme(self, scheme):
        if scheme == "yb":
            self.color_top_instr.rgb = (1, 1, 0)
            self.color_bottom_instr.rgb = (0, 0, 1)
        elif scheme == "rg":
            self.color_top_instr.rgb = (1, 0, 0)
            self.color_bottom_instr.rgb = (0, 1, 0)

        self.color_scheme = scheme

        app = App.get_running_app()
        app.config.set("color", "scheme", scheme)
        app.config.write()

    # ---------- DRAW ----------

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

    # ---------- GESTURE ----------

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


# ==================== MAIN LAYOUT ====================

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

    # ---------- MENU ----------

    def open_menu(self, *args):
        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12)
        )

        btn_yb = ToggleButton(
            text="Yellow / Blue",
            group="colors",
            state="down" if self.circles.color_scheme == "yb" else "normal",
            size_hint_y=None,
            height=dp(48)
        )
        btn_yb.bind(on_release=lambda *_: self.circles.set_color_scheme("yb"))

        btn_rg = ToggleButton(
            text="Red / Green",
            group="colors",
            state="down" if self.circles.color_scheme == "rg" else "normal",
            size_hint_y=None,
            height=dp(48)
        )
        btn_rg.bind(on_release=lambda *_: self.circles.set_color_scheme("rg"))

        layout.add_widget(btn_yb)
        layout.add_widget(btn_rg)

        btn_about = Button(
            text="About",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(16)
        )
        btn_about.bind(on_release=self.show_about)

        layout.add_widget(btn_about)

        self.menu_popup = Popup(
            title="Menu",
            content=layout,
            size_hint=(None, None),
            size=(dp(320), dp(300))
        )
        self.menu_popup.open()

    # ---------- ABOUT ----------

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

        Popup(
            title="About",
            content=label,
            size_hint=(None, None),
            size=(dp(420), dp(300))
        ).open()

    # ---------- EXIT ----------

    def exit_app(self, *args):
        self.circles.save_offset()
        App.get_running_app().stop()


# ==================== APP ====================

class MyApp(App):
    def build(self):
        self.config = ConfigParser()

        self.config_path = os.path.join(self.user_data_dir, "app.ini")
        self.config.read(self.config_path)

        # --- корректная инициализация ---
        if not self.config.has_section("color"):
            self.config.add_section("color")
        if not self.config.has_option("color", "scheme"):
            self.config.set("color", "scheme", "yb")

        if not self.config.has_section("circles"):
            self.config.add_section("circles")
        if not self.config.has_option("circles", "offset"):
            self.config.set("circles", "offset", "0")

        self.config.write()

        Window.clearcolor = (0, 0, 0, 1)
        return MainLayout()


MyApp().run()
