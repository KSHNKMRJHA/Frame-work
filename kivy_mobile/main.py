# -*- coding: utf-8 -*-
"""
FrameWork — Mobile Companion (Kivy)
======================================================
A lightweight, self-contained, cross-platform quiz + encyclopedia app that
runs identically on Windows/macOS/Linux desktops AND, when built with
Buildozer, on Android as a real installable .apk.

Run on desktop directly:
    pip install kivy
    python main.py

Build an Android APK:
    pip install buildozer cython
    buildozer -v android debug
    (see buildozer.spec in this folder, and README.md for full steps)
"""

import json
import os
import random

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window

from quiz_logic import generate_quiz

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "protocols.json")

Window.clearcolor = (0.06, 0.09, 0.16, 1)


def load_protocols():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


PROTOCOLS = load_protocols()
CATEGORIES = ["All"] + sorted(set(p["category"] for p in PROTOCOLS))


class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0.15, 0.39, 0.92, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(15)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16))
        root.add_widget(
            Label(text="[b]FrameWork[/b]", markup=True, font_size=dp(30), size_hint=(1, 0.3), halign="center")
        )
        root.add_widget(
            Label(
                text=f"{len(PROTOCOLS)} protocols across {len(CATEGORIES) - 1} categories",
                font_size=dp(14),
                size_hint=(1, 0.1),
                color=(0.6, 0.7, 0.85, 1),
            )
        )

        btn_quiz = StyledButton(text="Start Quiz", size_hint=(1, 0.15))
        btn_quiz.bind(on_release=lambda *_: setattr(self.manager, "current", "quiz_setup"))
        root.add_widget(btn_quiz)

        btn_browse = StyledButton(text="Browse Encyclopedia", size_hint=(1, 0.15))
        btn_browse.bind(on_release=lambda *_: setattr(self.manager, "current", "browse"))
        root.add_widget(btn_browse)

        btn_about = StyledButton(text="About", size_hint=(1, 0.15))
        btn_about.bind(on_release=lambda *_: setattr(self.manager, "current", "about"))
        root.add_widget(btn_about)

        self.add_widget(root)


class QuizSetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16))
        root.add_widget(Label(text="[b]Quiz Setup[/b]", markup=True, font_size=dp(22), size_hint=(1, 0.15)))

        root.add_widget(Label(text="Category:", size_hint=(1, 0.08)))
        self.cat_spinner = Spinner(text="All", values=CATEGORIES, size_hint=(1, 0.1))
        root.add_widget(self.cat_spinner)

        root.add_widget(Label(text="Number of questions:", size_hint=(1, 0.08)))
        self.n_spinner = Spinner(text="10", values=["5", "10", "15", "20"], size_hint=(1, 0.1))
        root.add_widget(self.n_spinner)

        start_btn = StyledButton(text="Start", size_hint=(1, 0.15))
        start_btn.bind(on_release=self.start_quiz)
        root.add_widget(start_btn)

        back_btn = Button(text="Back", size_hint=(1, 0.12))
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        root.add_widget(back_btn)

        self.add_widget(root)

    def start_quiz(self, *_):
        n = int(self.n_spinner.text)
        cat = self.cat_spinner.text
        quiz_screen = self.manager.get_screen("quiz")
        quiz_screen.load_quiz(cat, n)
        self.manager.current = "quiz"


class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = []
        self.idx = 0
        self.score = 0
        self.layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        self.add_widget(self.layout)

    def load_quiz(self, category, n):
        self.questions = generate_quiz(
            PROTOCOLS, n=n, seed=random.randint(0, 999999), category=category, difficulty=None
        )
        self.idx = 0
        self.score = 0
        self.render_question()

    def render_question(self):
        self.layout.clear_widgets()
        if self.idx >= len(self.questions):
            self.show_results()
            return
        q = self.questions[self.idx]
        header = Label(
            text=f"Question {self.idx + 1}/{len(self.questions)}  |  Score: {self.score}",
            size_hint=(1, 0.08),
            color=(0.6, 0.7, 0.85, 1),
        )
        self.layout.add_widget(header)

        scroll = ScrollView(size_hint=(1, 0.35))
        qlabel = Label(text=q["question"].replace("**", ""), size_hint_y=None, markup=False, font_size=dp(16))
        qlabel.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        qlabel.text_size = (Window.width - dp(48), None)
        scroll.add_widget(qlabel)
        self.layout.add_widget(scroll)

        for opt in q["options"]:
            b = StyledButton(text=opt, size_hint=(1, 0.13))
            b.bind(on_release=lambda inst, o=opt: self.answer(o))
            self.layout.add_widget(b)

    def answer(self, chosen):
        q = self.questions[self.idx]
        correct = chosen == q["answer"]
        if correct:
            self.score += 1
        popup_content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        msg = "Correct!" if correct else f"Incorrect. Answer: {q['answer']}"
        popup_content.add_widget(Label(text=msg, font_size=dp(16)))
        explain = Label(text=q["explain"], font_size=dp(13))
        explain.text_size = (dp(280), None)
        popup_content.add_widget(explain)
        next_btn = StyledButton(text="Next", size_hint=(1, 0.3))
        popup = Popup(title="Result", content=popup_content, size_hint=(0.85, 0.5))
        next_btn.bind(on_release=lambda *_: (popup.dismiss(), self.next_question()))
        popup_content.add_widget(next_btn)
        popup.open()

    def next_question(self):
        self.idx += 1
        self.render_question()

    def show_results(self):
        self.layout.clear_widgets()
        pct = 100 * self.score / max(1, len(self.questions))
        self.layout.add_widget(Label(text="[b]Quiz Complete![/b]", markup=True, font_size=dp(24)))
        self.layout.add_widget(Label(text=f"Score: {self.score}/{len(self.questions)} ({pct:.0f}%)", font_size=dp(18)))
        again_btn = StyledButton(text="Back to Menu", size_hint=(1, 0.15))
        again_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        self.layout.add_widget(again_btn)


class BrowseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(Label(text="[b]Encyclopedia[/b]", markup=True, font_size=dp(22), size_hint=(1, 0.1)))
        self.cat_spinner = Spinner(text="All", values=CATEGORIES, size_hint=(1, 0.1))
        self.cat_spinner.bind(text=self.refresh_list)
        root.add_widget(self.cat_spinner)

        self.scroll = ScrollView(size_hint=(1, 0.65))
        self.list_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        root.add_widget(self.scroll)

        back_btn = Button(text="Back", size_hint=(1, 0.1))
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        root.add_widget(back_btn)

        self.add_widget(root)
        self.refresh_list()

    def refresh_list(self, *_):
        self.list_layout.clear_widgets()
        cat = self.cat_spinner.text
        items = [p for p in PROTOCOLS if cat == "All" or p["category"] == cat]
        for p in items:
            b = Button(
                text=f"{p['name']}  ({p['year']})",
                size_hint_y=None,
                height=dp(44),
                background_normal="",
                background_color=(0.12, 0.16, 0.24, 1),
            )
            b.bind(on_release=lambda inst, proto=p: self.show_detail(proto))
            self.list_layout.add_widget(b)

    def show_detail(self, proto):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
        scroll = ScrollView()
        lbl = Label(
            text=(
                f"[b]{proto['name']}[/b]\n\nCategory: {proto['category']}\nYear: {proto['year']}\n"
                f"Inventor: {proto['inventor']}\n\n{proto['description']}\n\n"
                f"How it works: {proto.get('how_it_works', '')}\n\nSpeed: {proto.get('speed', '-')}"
            ),
            markup=True,
            size_hint_y=None,
            font_size=dp(14),
        )
        lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        lbl.text_size = (Window.width - dp(64), None)
        scroll.add_widget(lbl)
        content.add_widget(scroll)
        popup = Popup(title="Protocol Detail", content=content, size_hint=(0.92, 0.85))
        popup.open()


class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(14))
        root.add_widget(
            Label(
                text="[b]FrameWork[/b] v1.0.0\nMobile Companion\n\n"
                "Built with Kivy — runs on Windows, macOS, Linux, and Android.\n\n"
                "Full desktop/web edition (Streamlit) includes diagrams, mind maps,\n"
                "timelines, and the Science & Math Lab.\n\n"
                "Created by Kishan J. · Design by Piston\n"
                "Made with love and AI\n\n"
                "MIT Licensed. Free to use, modify and redistribute.\n\n"
                "github.com/KSHNKMRJHA/Frame-work",
                markup=True,
                font_size=dp(15),
                halign="center",
            )
        )
        back_btn = StyledButton(text="Back", size_hint=(1, 0.15))
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "home"))
        root.add_widget(back_btn)
        self.add_widget(root)


class AcademyApp(App):
    def build(self):
        self.title = "FrameWork"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(QuizSetupScreen(name="quiz_setup"))
        sm.add_widget(QuizScreen(name="quiz"))
        sm.add_widget(BrowseScreen(name="browse"))
        sm.add_widget(AboutScreen(name="about"))
        return sm


if __name__ == "__main__":
    AcademyApp().run()
