from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.resources import resource_find
from kivy.config import ConfigParser
from kivy.uix.image import Image
from kivy.clock import Clock

import os
import json

# ===== КОНСТАНТЫ =====
CIRCLE_RADIUS_RATIO = 0.25
BG_COLOR = (0, 0, 0)


def rgb255(r, g, b):
    return (r / 255.0, g / 255.0, b / 255.0)


def read_text_resource(filename, fallback_text):
    path = resource_find(filename)
    if not path:
        return fallback_text
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_color_schemes_from_file(filename="config.json"):
    """
    Ожидаемый формат JSON (пример):
    [
      {"id":"yb","title":"Yellow / Blue","top":[255,255,0],"bottom":[0,0,255]},
      {"id":"rg","title":"Red / Green","top":[255,0,0],"bottom":[0,255,0]},
      {"id":"rc","title":"Red / Cyan","top":[255,0,0],"bottom":[0,255,255]}
    ]
    """
    path = resource_find(filename)
    if not path:
        return None, None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes = {}
    order = []
    for item in data:
        sid = item["id"]
        title = item["title"]
        top = item["top"]
        bottom = item["bottom"]

        schemes[sid] = {
            "title": title,
            "top_rgb": rgb255(top[0], top[1], top[2]),
            "bottom_rgb": rgb255(bottom[0], bottom[1], bottom[2]),
        }
        order.append(sid)

    return schemes, order


def default_color_schemes():
    schemes = {
        "yb": {
            "title": "Yellow / Blue",
            "top_rgb": rgb255(255, 255, 0),
            "bottom_rgb": rgb255(0, 0, 255),
        },
        "rg": {
            "title": "Red / Green",
            "top_rgb": rgb255(255, 0, 0),
            "bottom_rgb": rgb255(0, 255, 0),
        },
        "rc": {
            "title": "Red / Cyan",
            "top_rgb": rgb255(255, 0, 0),
            "bottom_rgb": rgb255(0, 255, 255),
        },
    }
    order = ["yb", "rg", "rc"]
    return schemes, order


# ==================== TWO CIRCLES ====================

class TwoCirclesWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.offset = None
        self.start_touch_y = None
        self.start_offset = None

        self.color_scheme = "yb"  # id

        with self.canvas:
            Color(*BG_COLOR)
            self.bg = Rectangle()

            self.color_top_instr = Color(1, 1, 0)      # будет перезаписано схемой
            self.circle_top = Ellipse()

            self.color_bottom_instr = Color(0, 0, 1)   # будет перезаписано схемой
            self.circle_bottom = Ellipse()

        self.bind(size=self.update, pos=self.update)
        self.load_state()

    # ---------- STATE ----------

    def load_state(self):
        app = App.get_running_app()

        scheme = app.config.get("color", "scheme")
        if scheme not in app.color_schemes:
            scheme = app.color_schemes_order[0]

        self.set_color_scheme(scheme)

        saved_offset = float(app.config.get("circles", "offset"))
        if saved_offset > 0:
            self.offset = saved_offset

    def save_offset(self):
        app = App.get_running_app()
        app.config.set("circles", "offset", str(self.offset))
        app.config.write()

    # ---------- COLORS ----------

    def set_color_scheme(self, scheme_id):
        app = App.get_running_app()
        if scheme_id not in app.color_schemes:
            scheme_id = app.color_schemes_order[0]

        scheme = app.color_schemes[scheme_id]

        self.color_top_instr.rgb = scheme["top_rgb"]
        self.color_bottom_instr.rgb = scheme["bottom_rgb"]
        self.color_scheme = scheme_id

        app.config.set("color", "scheme", scheme_id)
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

    # ---------- GESTURE (ONE FINGER) ----------

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

        logo = Image(
            source="logo.png",
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            pos_hint={"center_x": 0.5, "top": 1},
            allow_stretch=False,
            keep_ratio=True
        )
        
        logo.bind(
            size=lambda inst, *_: setattr(inst, "x", (content.width - inst.width) / 2)
        )
                
        self.add_widget(logo)

    # ---------- MENU ----------

    def open_menu(self, *args):
        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12)
        )

        btn_colors = Button(
            text="Colors",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(16)
        )
        btn_colors.bind(on_release=self.open_colors_submenu)

        btn_info = Button(
            text="Info",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(16)
        )
        btn_info.bind(on_release=self.show_info)

        btn_about = Button(
            text="About",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(16)
        )
        btn_about.bind(on_release=self.show_about)

        layout.add_widget(btn_colors)
        layout.add_widget(btn_info)
        layout.add_widget(btn_about)

        btn_back = Button(
            text="Back",
            size_hint_y=None,
            height=dp(48),
            font_size=dp(16)
        )
        btn_back.bind(on_release=lambda *_: self.menu_popup.dismiss())
        
        layout.add_widget(btn_back)        
        
        self.menu_popup = Popup(
            title="Menu",
            content=layout,
            size_hint=(None, None),
            size=(dp(320), dp(320))
        )
        self.menu_popup.open()

    def open_colors_submenu(self, *args):
        if hasattr(self, "menu_popup"):
            self.menu_popup.dismiss()

        app = App.get_running_app()

        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12)
        )

        for scheme_id in app.color_schemes_order:
            title = app.color_schemes[scheme_id]["title"]
            btn = ToggleButton(
                text=title,
                group="colors",
                state="down" if self.circles.color_scheme == scheme_id else "normal",
                size_hint_y=None,
                height=dp(52)
            )
            btn.bind(on_release=lambda _btn, sid=scheme_id: self.circles.set_color_scheme(sid))
            layout.add_widget(btn)
            #  End of cycle
            
        btn_back = Button(
            text="Back",
            size_hint_y=None,
            height=dp(48),
            font_size=dp(16)
        )
        btn_back.bind(on_release=lambda *_: self.colors_popup.dismiss())
        
        layout.add_widget(btn_back)        
        
        self.colors_popup = Popup(
            title="Colors",
            content=layout,
            size_hint=(0.6, 0.85)
        )
        self.colors_popup.open()

    # ---------- ABOUT ----------

    def show_about(self, *args):
        if hasattr(self, "menu_popup"):
            self.menu_popup.dismiss()
    
        text = read_text_resource("about.txt", "About file not found")
    
        scroll = ScrollView(do_scroll_x=False)
    
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
            padding=dp(12)
        )
    
        # ----- текст -----
        label = Label(
            text=text,
            markup=True,
            halign="center",
            valign="top",
            size_hint_y=None
        )
        label.bind(texture_size=lambda inst, size: setattr(inst, "height", size[1]))
        content.add_widget(label)
    
        # ----- логотип внизу (по центру) -----
        logo = Image(
            source="logo.png",
            size_hint_y=None,
            height=dp(56),
            allow_stretch=True,
            keep_ratio=True
        )
        content.add_widget(logo)
    
        # корректная высота контейнера
        content.bind(minimum_height=content.setter("height"))
    
        scroll.add_widget(content)
    
        # ---- контейнер с кнопкой Back ----
        root = BoxLayout(orientation="vertical")
    
        popup = Popup(
            title="About",
            size_hint=(0.75, 0.75)
        )
    
        btn_back = Button(
            text="Back",
            size_hint_y=None,
            height=dp(48)
        )
        btn_back.bind(on_release=lambda *_: popup.dismiss())
    
        root.add_widget(scroll)
        root.add_widget(btn_back)
    
        popup.content = root
        popup.open()
            
    # ---------- INFO (SCROLL + MARKUP) ----------

    def show_info(self, *args):
        if hasattr(self, "menu_popup"):
            self.menu_popup.dismiss()
    
        text = read_text_resource("info.txt", "info.txt not found")
    
        scroll = ScrollView(do_scroll_x=False)
    
        label = Label(
            text=text,
            markup=True,
            halign="left",
            valign="top",
            size_hint_y=None
        )
    
        def _update_wrap(*_):
            label.text_size = (max(0, scroll.width - dp(24)), None)
    
        label.bind(texture_size=lambda inst, size: setattr(inst, "height", size[1]))
        scroll.bind(width=_update_wrap)
        _update_wrap()
    
        scroll.add_widget(label)
    
        root = BoxLayout(orientation="vertical")
    
        popup = Popup(
            title="Impossible Colors (Forbidden Colors)",
            size_hint=(0.9, 0.9)
        )
    
        btn_back = Button(
            text="Back",
            size_hint_y=None,
            height=dp(48)
        )
        btn_back.bind(on_release=lambda *_: popup.dismiss())
    
        root.add_widget(scroll)
        root.add_widget(btn_back)
    
        popup.content = root
        popup.open()
    
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

        if not self.config.has_section("color"):
            self.config.add_section("color")
        if not self.config.has_option("color", "scheme"):
            self.config.set("color", "scheme", "yb")

        if not self.config.has_section("circles"):
            self.config.add_section("circles")
        if not self.config.has_option("circles", "offset"):
            self.config.set("circles", "offset", "0")

        # --- загрузка цветовых схем из файла проекта ---
        schemes, order = load_color_schemes_from_file("config.json")
        if not schemes:
            schemes, order = default_color_schemes()

        self.color_schemes = schemes
        self.color_schemes_order = order

        # --- валидация сохранённой схемы ---
        saved_scheme = self.config.get("color", "scheme")
        if saved_scheme not in self.color_schemes:
            self.config.set("color", "scheme", self.color_schemes_order[0])

        self.config.write()

        Window.clearcolor = (0, 0, 0, 1)
        
        Clock.schedule_once(self.force_redraw, 0)
        return MainLayout()

    def force_redraw(self, *args):
        Window.dispatch("on_draw")
        Window.canvas.ask_update()
        
MyApp().run()
