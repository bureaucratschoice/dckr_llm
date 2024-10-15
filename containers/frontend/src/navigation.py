#!/usr/bin/env python3
from typing import List, Tuple
from nicegui import app,context, ui, events
import os
#from home import home
#from chat import chat
#from pdf import pdfpage


def navigation():
    anchor_style = r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}'
    ui.add_head_html(f'<style>{anchor_style}</style>')
    title = os.getenv('APP_TITLE',default="dckr_chat")
    ui.page_title(title)
    with ui.header().classes(replace='row items-center') as header:
        with ui.row():

            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        with ui.row():
            ui.image('/app/static/logo.jpeg').classes('w-64 h-32 absolute-right')
    with ui.left_drawer().classes('bg-blue-100') as left_drawer:
        ui.link("Home","/")
        tochat = os.getenv('TOCHAT',default="Zum Chat")
        ui.link(tochat, "/chat")
        topdf = os.getenv('TOPDF',default="Zu den PDF-Werkzeugen")
        ui.link(topdf, "/pdf")
        