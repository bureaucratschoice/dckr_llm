#!/usr/bin/env python3
from typing import List, Tuple
from nicegui import app,context, ui, events
from helpers.random_words import get_random_word_string

def statistics():
    navigation()
    title = os.getenv('APP_TITLE',default=cfg.get_config('frontend','app_title',default="MWICHT"))
    categories = ['visit','chat','pdf_question','pdf_summary','max_queue']
    ui.button(on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login')), icon='logout').props('outline round')
    for c in categories:
            
            ui.label('CSS').style('color: #000').set_text(c)
            dates, values = statistic.getEventStat(c)
            columns = [
                {'name': 'date', 'label': 'Date', 'field': 'date', 'required': True, 'align': 'left'},
                {'name': 'value', 'label': c, 'field': 'value', 'sortable': True},
            ]
            rows = []
            for d,v in zip(dates,values):
                rows.append({'date': d, 'value': v})
                
            ui.table(columns=columns, rows=rows, row_key='name')