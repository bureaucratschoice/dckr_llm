#!/usr/bin/env python3
from typing import List, Tuple
from nicegui import app,context, ui, events
from helpers.random_words import get_random_word_string

import os


def home():
    navigation()
    statistic.addEvent('visit')
    title = os.getenv('APP_TITLE',default=cfg.get_config('frontend','app_title',default="MWICHT"))
        
    with ui.column().classes('absolute-center'):
        with ui.row():
            ui.image('/app/static/home_background1.jpeg').classes('w-60 h-60')
            ui.image('/app/static/home_background2.jpeg').classes('w-60 h-60')
        with ui.row():
            ui.image('/app/static/home_background3.jpeg').classes('w-60 h-60')
            ui.image('/app/static/home_background4.jpeg').classes('w-60 h-60')
