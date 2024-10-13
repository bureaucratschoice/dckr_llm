#!/usr/bin/env python3
from typing import List, Tuple, Optional

from nicegui import app,context, ui, events, Client
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import time
from uuid import uuid4
import json


from home import home
from navigation import navigation
from chat import chat
from management import mngmt
from pdf import pdf
from statistics import statistics
from login import login


class InputText:
    def __init__(self):
        self.text = ""

inputText = InputText()

class PDFReady:
    def __init__(self):
        self.ready = False
        self.answered = False
        self.ready_to_upload = True


def assign_uuid_if_missing():
    if not 'chat_job' in app.storage.user or not app.storage.user['chat_job']:
        app.storage.user['chat_job'] = uuid4()
    if not 'pdf_job' in app.storage.user or not app.storage.user['pdf_job']:
        app.storage.user['pdf_job'] = uuid4()
    if not 'pdf_ready' in app.storage.user or not app.storage.user['pdf_ready']:
        app.storage.user['pdf_ready']= {'ready':False,'answered':False,'ready_to_upload':True}


'''Authentication for management tasks via SUPERTOKEN'''
passwords = {'mngmt': os.getenv('SUPERTOKEN',default="PLEASE_CHANGE_THIS_PLEASE")}

unrestricted_page_routes = {'/login','/','/chat','/pdf'}


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)


app.add_middleware(AuthMiddleware)
'''End of Authentication'''

def init(fastapi_app: FastAPI,jobStat,taskQueue,cfg,statistic) -> None:
    
    @ui.page('/chat')
    def call_chat():
        chat()
                
    @ui.page('/')
    def call_home():
        home()           

    @ui.page('/management')
    def call_mngmt():
        mngmt()
        

    @ui.page('/login')
    def call_login():
        login()

    @ui.page('/statistic')
    def call_statistics():
        statistics()
    @ui.page('/pdf')
    def call_pdf():
        pdf()  

    ui.run_with(
        fastapi_app,
        storage_secret = uuid4(),
    )
