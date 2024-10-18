#!/usr/bin/env python3
from typing import List, Tuple
from nicegui import app,context, ui, events
import os

from navigation import navigation 
from jobtools import ChatJob, RoleToggle
from api_calls import ChatClient

def chat():
    sysprompt = "Du bist ein hilfreicher KI-Assistent."
    if not 'ChatJob' in app.storage.user:
        app.storage.user['ChatJob'] = ChatJob(sys_prompt="TEST",messages=[]).to_dict()
    chat_job = ChatJob.from_dict(app.storage.user['ChatJob']) 
    if not 'RoleToogle' in app.storage.user:
        app.storage.user['RoleToogle'] = RoleToggle(assistant=os.getenv('ASSISTANT',default="Assistent:in"),user=os.getenv('YOU',default="Sie")).to_dict()
    role_toggle = RoleToggle.from_dict(app.storage.user['RoleToogle'])

    client = ChatClient()

    greeting = os.getenv('GREETING',"Achtung, prüfen Sie jede Antwort bevor Sie diese in irgendeiner Form weiterverwenden. Je länger Ihre Frage ist bzw. je länger der bisherige Chatverlauf, desto länger brauche ich zum lesen. Es kann daher dauern, bis ich anfange Ihre Antwort zu schreiben. Die Länge der Warteschlange ist aktuell:" )
   
    thinking: bool = False
    timer = ui.timer(1.0, lambda: chat_messages.refresh())
    you = os.getenv('YOU',default="Sie")
    @ui.refreshable
    def chat_messages() -> None:
        result = client.get_completion(chat_job.get_uuid())
        chat_job.set_completion(result['completion'])
        chat_job.set_status(result['status'])

        for msg in chat_job.get_messages():
            name = role_toggle.get_acting()
            ui.chat_message(text=msg, name=name, sent=name == you)
                
        name = role_toggle.get_acting()
        ui.chat_message(text=chat_job.get_completion(), name=name, sent=name == you)

        if chat_job.get_status() == 'processing':
            thinking = True
            timer.activate()
                    
        else:
            thinking = False
            timer.activate()
            if chat_job.get_status()== 'finished':
                chat_job.append_message()
                timer.deactivate()
            

        if thinking:
            ui.spinner(size='3rem').classes('self-center')
        #if context.get_client().has_socket_connection:
        #    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

        
    #TODO
    def delete_chat() -> None:
        app.storage.user['input'] = ""
        app.storage.user['chat_job'] = 0
        chat_messages.refresh()
    
    #TODO
    def copy_data():

        if 'answer' in app.storage.user['chat_job']:
            text = app.storage.user['chat_job']['answer']
            ui.run_javascript('navigator.clipboard.writeText(`' + text + '`)', timeout=5.0)



    async def send() -> None:
        user_input = app.storage.user['input']
        chat_job.append_chunk(user_input)
        chat_job.append_message()

        text.value = ''
        app.storage.user['input'] = ''

        uuid = client.send_chat(sysprompt,chat_job.get_messages)
        chat_job.set_uuid()

        timer.activate()
        chat_messages.refresh()
            
    navigation()
    # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
    ui.query('.q-page').classes('flex')
    ui.query('.nicegui-content').classes('w-full')
        
    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('Chat')

    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        with ui.tab_panel(chat_tab).classes('items-stretch'):
                
            chat_messages()


    with ui.footer().classes('bg-white'):
        with ui.column().classes('w-full max-w-3xl mx-auto my-6'):
            with ui.row().classes('w-full no-wrap items-center'):
                placeholder = 'message' 
                text = ui.textarea(placeholder=placeholder).props('rounded outlined input-class=mx-3').props('clearable') \
                    .classes('w-full self-center').bind_value(app.storage.user, 'input').on('keydown.enter', send)
                send_btn = ui.button(icon="send", on_click=lambda: send())
                copy_btn = ui.button(icon="content_copy", on_click=lambda: copy_data())
                delete_btn = ui.button(icon="delete_forever", on_click=lambda: delete_chat())
            
                
    