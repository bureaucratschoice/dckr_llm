#!/usr/bin/env python3
from typing import List, Tuple
from nicegui import app,context, ui, events
import os

from navigation import navigation 

def chat():
    assi = os.getenv('ASSISTANT',default=cfg.get_config('frontend','assistant',default="Assistent:in"))
    you = os.getenv('YOU',default=cfg.get_config('frontend','you',default="Sie"))
    greeting = os.getenv('GREETING',default=cfg.get_config('frontend','chat-greeting',default="Achtung, prüfen Sie jede Antwort bevor Sie diese in irgendeiner Form weiterverwenden. Je länger Ihre Frage ist bzw. je länger der bisherige Chatverlauf, desto länger brauche ich zum lesen. Es kann daher dauern, bis ich anfange Ihre Antwort zu schreiben. Die Länge der Warteschlange ist aktuell: "))
    pdf_greeting = os.getenv('PDFGREETING',default=cfg.get_config('frontend','pdf-greeting',default="Laden Sie ein PDF hoch, damit ich Ihnen Fragen hierzu beantworten kann. Achtung, prüfen Sie jede Antwort bevor Sie diese in irgendeiner Form weiterverwenden. Die Länge der Warteschlange ist aktuell: "))
    pdf_processed = os.getenv('PDFPROC',default=cfg.get_config('frontend','pdf-preprocessing',default="Ihr PDF wird gerade verarbeitet. Der aktuelle Status ist: "))
    
    messages: List[Tuple[str, str]] = [] 
    thinking: bool = False
    timer = ui.timer(1.0, lambda: chat_messages.refresh())
    assign_uuid_if_missing()
    @ui.refreshable
    def chat_messages() -> None:
        assign_uuid_if_missing()
        messages: List[Tuple[str, str]] = [] 
        messages.append((assi, greeting + str(jobStat.countQueuedJobs())))
        answers = []
        questions = []
        status = jobStat.getJobStatus(app.storage.browser['id'],app.storage.user['chat_job'])
        if 'job_type' in status and status['job_type'] == 'chat' :

            if 'answer' in status:
                answers = status['answer']
            if 'prompt' in status:
                questions = status['prompt']
        i_q = 0
        i_a = 0
           
        while i_q < len(questions) and questions[i_q]:

            messages.append((you,questions[i_q]))
            if i_a < len(answers) and answers[i_q]:
                messages.append((assi,answers[i_q]))
            i_q += 1
            i_a += 1
        for name, text in messages:
            ui.chat_message(text=text, name=name, sent=name == you)
                
        if 'status' in status:
            if status['status'] == 'processing':
                thinking = True
                timer.activate()
                    
            else:
                thinking = False
                timer.activate()
            if status['status'] == 'finished':
                timer.deactivate()
            
        else:
            thinking = False
            timer.activate()
        if thinking:
            ui.spinner(size='3rem').classes('self-center')
        if context.get_client().has_socket_connection:
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

        
    def update_response() -> None:
            
        answers = []
        questions = []
        if 'answer' in status:
            answers = status['answer']
        if 'prompt' in status:
            questions = status['prompt']
            

        i_q = 0
        i_a = 0
            
        while i_q < len(questions):
            messages.append((you,questions[i_q]))
            if i_a < len(answers):
                messages.append((assi,answers[i_q]))
            i_q += 1
            i_a += 1

    def delete_chat() -> None:
        assign_uuid_if_missing()
        jobStat.removeJob(app.storage.browser['id'],app.storage.user['chat_job'])
        app.storage.user['text'] = ""
        app.storage.user['chat_job'] = uuid4()
        chat_messages.refresh()
        
    def copy_data():
        if 'answer' in jobStat.getJobStatus(app.storage.browser['id'],app.storage.user['chat_job']):
            text = jobStat.getJobStatus(app.storage.browser['id'],app.storage.user['chat_job'])['answer'][-1]
            ui.run_javascript('navigator.clipboard.writeText(`' + text + '`)', timeout=5.0)

    def reset_config():
        app.storage.user['temperature'] = os.getenv('TEMPERATURE',default=cfg.get_config('model','temperature',default=0.7))*100
        app.storage.user['max_tokens'] = os.getenv('MAX_TOKENS',default=cfg.get_config('model','max_tokens',default=1024))
        app.storage.user['top_k'] = os.getenv('TOP_K',default=cfg.get_config('model','top_k',default=40))
        app.storage.user['top_p'] = os.getenv('TOP_P',default=cfg.get_config('model','top_p',default=0.8))*100
        app.storage.user['repeat_penalty'] = os.getenv('REPEAT_PENALTY',default=cfg.get_config('model','repeat_penalty',default=1.15))*100

    async def send() -> None:
        statistic.addEvent('chat')
        assign_uuid_if_missing()
        message = app.storage.user['text']
        custom_config = {'temperature':app.storage.user['temperature']/100,'max_tokens':app.storage.user['max_tokens'],'top_k':app.storage.user['top_k'],'top_p':app.storage.user['top_p']/100,'repeat_penalty':app.storage.user['repeat_penalty']/100}
        text.value = ''
        jobStat.addJob(app.storage.browser['id'],app.storage.user['chat_job'],message,custom_config,'chat')
        job = {'token':app.storage.browser['id'],'uuid':app.storage.user['chat_job']}
        try:
            taskQueue.put(job)
        except:
            jobStat.updateStatus(app.storage.browser['id'],app.storage.user['chat_job'],"failed") 

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
                    .classes('w-full self-center').bind_value(app.storage.user, 'text').on('keydown.enter', send)
                send_btn = ui.button(icon="send", on_click=lambda: send())
                copy_btn = ui.button(icon="content_copy", on_click=lambda: copy_data())
                delete_btn = ui.button(icon="delete_forever", on_click=lambda: delete_chat())
            
            with ui.row().classes('w-full no-wrap items-center'):
                config_lbl = ui.label('CSS').style('color: #000') 
                config_lbl.set_text('custom config: ')  
                v = ui.checkbox('custom config', value=False)
            with ui.row().classes('w-full no-wrap items-center').bind_visibility_from(v, 'value'):
                temp_lbl = ui.label('CSS').style('color: #000')
                temp_lbl.set_text('Temperature: ')
                temp_sld = ui.slider(min=0, max=100, value=os.getenv('TEMPERATURE',default=cfg.get_config('model','temperature',default=0.7))*100).bind_value(app.storage.user, 'temperature')
                temp_val_lbl = ui.label('CSS').style('color: #000')
                temp_val_lbl.bind_text_from(app.storage.user, 'temperature', lambda x: x/100)

            with ui.row().classes('w-full no-wrap items-center').bind_visibility_from(v, 'value'):
                max_tokens_lbl = ui.label('CSS').style('color: #000')
                max_tokens_lbl.set_text('Max Tokens: ')
                max_tokens_sld = ui.slider(min=0, max=4096, value=os.getenv('MAX_TOKENS',default=cfg.get_config('model','max_tokens',default=1024))).bind_value(app.storage.user, 'max_tokens')
                max_tokens_val_lbl = ui.label('CSS').style('color: #000')
                max_tokens_val_lbl.bind_text_from(app.storage.user, 'max_tokens')

            with ui.row().classes('w-full no-wrap items-center').bind_visibility_from(v, 'value'):
                top_k_lbl = ui.label('CSS').style('color: #000') 
                top_k_lbl.set_text('Top k: ')
                top_k_sld = ui.slider(min=0, max=100, value=os.getenv('TOP_K',default=cfg.get_config('model','top_k',default=40))).bind_value(app.storage.user, 'top_k')
                top_k_val_lbl = ui.label('CSS').style('color: #000') 
                top_k_val_lbl.bind_text_from(app.storage.user, 'top_k')

            with ui.row().classes('w-full no-wrap items-center').bind_visibility_from(v, 'value'):
                top_p_lbl = ui.label('CSS').style('color: #000') 
                top_p_lbl.set_text('Top p: ')
                top_p_sld = ui.slider(min=0, max=100, value=os.getenv('TOP_P',default=cfg.get_config('model','top_p',default=0.8))*100).bind_value(app.storage.user, 'top_p')
                top_p_val_lbl = ui.label('CSS').style('color: #000') 
                top_p_val_lbl.bind_text_from(app.storage.user, 'top_p',lambda x: x/100)

            with ui.row().classes('w-full no-wrap items-center').bind_visibility_from(v, 'value'):
                repeat_penalty_lbl = ui.label('CSS').style('color: #000')
                repeat_penalty_lbl.set_text('Repeat penalty: ')
                repeat_penalty_sld = ui.slider(min=0, max=200, value=os.getenv('REPEAT_PENALTY',default=cfg.get_config('model','repeat_penalty',default=1.15))*100).bind_value(app.storage.user, 'repeat_penalty')
                repeat_penalty_val_lbl = ui.label('CSS').style('color: #000') 
                repeat_penalty_val_lbl.bind_text_from(app.storage.user, 'repeat_penalty',lambda x: x/100)
                
            with ui.row().classes('w-full no-wrap items-center').bind_visibility_from(v, 'value'):                   
                reset_btn = ui.button(text="reset", on_click=lambda: reset_config())
                
    