#!/usr/bin/env python3

from typing import List, Tuple, Optional  # UNUSED, consider removing

from nicegui import app, ui, events  # `context` and `Client` UNUSED, remove
from datetime import datetime  # UNUSED, remove if not needed in future logic
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import time  # UNUSED, remove if not used later
from uuid import uuid4
import json  # UNUSED, remove if JSON parsing is unnecessary

# Importing modules specific to app components
from home import home
from navigation import navigation  # UNUSED, remove if not invoked
from chat import chat
from management import mngmt
from pdf import pdf
from statistics import statistics
from login import login

class InputText:
    """Class to manage user input text."""
    def __init__(self):
        self.text = ""

inputText = InputText()  # Instance of InputText used globally

class PDFReady:
    """Class to manage PDF state tracking."""
    def __init__(self):
        self.ready = False
        self.answered = False
        self.ready_to_upload = True

def assign_uuid_if_missing():
    """Assigns UUIDs to the user's chat and PDF sessions if they don't exist."""
    user_storage = app.storage.user

    if not user_storage.get('chat_job'):
        user_storage['chat_job'] = uuid4()
    
    if not user_storage.get('pdf_job'):
        user_storage['pdf_job'] = uuid4()
    
    if not user_storage.get('pdf_ready'):
        user_storage['pdf_ready'] = {
            'ready': False,
            'answered': False,
            'ready_to_upload': True
        }

# Authentication for management tasks via SUPERTOKEN
passwords = {'mngmt': os.getenv('SUPERTOKEN', default="PLEASE_CHANGE_THIS_PLEASE")}
unrestricted_page_routes = {'/login', '/', '/chat', '/pdf'}

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce authentication on restricted routes.
    Redirects unauthenticated users to the login page.
    """
    async def dispatch(self, request: Request, call_next):
        user_storage = app.storage.user

        if not user_storage.get('authenticated', False):
            if (
                request.url.path in Client.page_routes.values() and
                request.url.path not in unrestricted_page_routes
            ):
                # Remember the user's intended destination
                user_storage['referrer_path'] = request.url.path
                return RedirectResponse('/login')

        return await call_next(request)

# Add authentication middleware to the app
app.add_middleware(AuthMiddleware)

def init(fastapi_app: FastAPI, jobStat, taskQueue, cfg, statistic) -> None:
    """
    Initializes the app with page routes and runs it using the provided FastAPI app.

    Args:
        fastapi_app (FastAPI): The FastAPI app instance.
        jobStat: Job statistics object.
        taskQueue: Queue for managing background tasks.
        cfg: Configuration object.
        statistic: Statistics object for tracking metrics.
    """
    @ui.page('/chat')
    def call_chat():
        """Handles chat page requests."""
        chat()

    @ui.page('/')
    def call_home():
        """Handles home page requests."""
        home()

    @ui.page('/management')
    def call_mngmt():
        """Handles management page requests."""
        mngmt()

    @ui.page('/login')
    def call_login():
        """Handles login page requests."""
        login()

    @ui.page('/statistic')
    def call_statistics():
        """Handles statistics page requests."""
        statistics()

    @ui.page('/pdf')
    def call_pdf():
        """Handles PDF page requests."""
        pdf()

    # Run the app with FastAPI integration
    ui.run_with(
        fastapi_app,
        storage_secret=uuid4(),
    )
