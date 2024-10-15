#!/usr/bin/env python3
from typing import List, Tuple
from nicegui import app,context, ui, events
import os

from navigation import navigation 

def home():
    navigation()
   
    title = os.getenv('APP_TITLE',default="dckr_llm")
        
    with ui.column().classes('absolute-center'):
        with ui.row():
            ui.image('/app/static/home_background1.jpeg').classes('w-60 h-60')
            ui.image('/app/static/home_background2.jpeg').classes('w-60 h-60')
        with ui.row():
            ui.image('/app/static/home_background3.jpeg').classes('w-60 h-60')
            ui.image('/app/static/home_background4.jpeg').classes('w-60 h-60')
