from typing import List, Tuple
from nicegui import app,context, ui, events


from navigation import navigation 

def pdfpage():
    assi = os.getenv('ASSISTANT',default=cfg.get_config('frontend','assistant',default="Assistent:in"))
    you = os.getenv('YOU',default=cfg.get_config('frontend','you',default="Sie"))
    greeting = os.getenv('GREETING',default=cfg.get_config('frontend','chat-greeting',default="Achtung, prüfen Sie jede Antwort bevor Sie diese in irgendeiner Form weiterverwenden. Je länger Ihre Frage ist bzw. je länger der bisherige Chatverlauf, desto länger brauche ich zum lesen. Es kann daher dauern, bis ich anfange Ihre Antwort zu schreiben. Die Länge der Warteschlange ist aktuell: "))
    pdf_greeting = os.getenv('PDFGREETING',default=cfg.get_config('frontend','pdf-greeting',default="Laden Sie ein PDF hoch, damit ich Ihnen Fragen hierzu beantworten kann. Achtung, prüfen Sie jede Antwort bevor Sie diese in irgendeiner Form weiterverwenden. Die Länge der Warteschlange ist aktuell: "))
    pdf_processed = os.getenv('PDFPROC',default=cfg.get_config('frontend','pdf-preprocessing',default="Ihr PDF wird gerade verarbeitet. Der aktuelle Status ist: "))

    pdfmessages: List[Tuple[str, str]] = [] 
    thinking: bool = False
    timer = ui.timer(1.0, lambda: pdf_messages.refresh())
    assign_uuid_if_missing()
    pdf_ready = app.storage.user['pdf_ready']
    @ui.refreshable
    def pdf_messages() -> None:
        assign_uuid_if_missing()
        pdfmessages: List[Tuple[str, str]] = [] 
        pdfmessages.append((assi, pdf_greeting + str(jobStat.countQueuedJobs())))
        answers = []
        questions = []
        status = jobStat.getJobStatus(app.storage.browser['id'],app.storage.user['pdf_job'])
        if 'job_type' in status and status['job_type'] == 'pdf_processing' and 'status' in status:
            pdfmessages.append((assi, pdf_processed + str(status['status'])))
            if not status['status'] == 'finished':
                pdf_ready['ready'] = False
                    
            else:
                pdf_ready['ready'] = True
                pdf_ready['answered'] = True
                    

        if 'job_type' in status and status['job_type'] == 'pdf_chat':
            if 'status' in status and status['status'] == 'finished':
                pdf_ready['answered'] = True
            else:
                    
                pdf_ready['answered'] = False
            if 'prompt' in status:
                questions = status['prompt']
            if 'answer' in status:
                answers = status['answer']

                
            
        if 'job_type' in status and status['job_type'] == 'pdf_summarize':
            if 'status' in status and status['status'] == 'finished':
                pdf_ready['answered'] = True
            else:
                pdf_ready['answered'] = False
            if 'answer' in status:
                answers = status['answer']
        i_q = 0
        i_a = 0
        output_fin = False
        while not output_fin:
            if i_q < len(questions):
                if questions[i_q]:
                    pdfmessages.append((you,questions[i_q]))
                    i_q += 1
                else:
                    i_q += 1
                    continue
            if i_a < len(answers):
                if answers[i_a]:
                    pdfmessages.append((assi,answers[i_a]))
                    i_a += 1
                else:
                    i_a += 1
                    continue
            if i_q >= len(questions) and i_a >= len(answers):
                output_fin = True
            
        for name, text in pdfmessages:
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
        app.storage.user['pdf_ready'] = pdf_ready

    def delete_chat() -> None:
        assign_uuid_if_missing()
        jobStat.removeJob(app.storage.browser['id'],app.storage.user['pdf_job'])
        app.storage.user['pdf_question'] = ""
        app.storage.user['pdf_job'] = uuid4()
        pdf_ready['ready'] = False
        pdf_ready['answered'] = False
        pdf_ready['ready_to_upload'] = True
        app.storage.user['pdf_ready'] = pdf_ready
        pdf_messages.refresh()

    def copy_data():
        if 'answer' in jobStat.getJobStatus(app.storage.browser['id'],app.storage.user['pdf_job']):
            text = jobStat.getJobStatus(app.storage.browser['id'],app.storage.user['pdf_job'])['answer'][-1]
            ui.run_javascript('navigator.clipboard.writeText(`' + text + '`)', timeout=5.0)

    async def send() -> None:
        statistic.addEvent('pdf_question')
        assign_uuid_if_missing()
        message = app.storage.user['pdf_question']
        #custom_config = {'temperature':app.storage.user['temperature']/100,'max_tokens':app.storage.user['max_tokens'],'top_k':app.storage.user['top_k'],'top_p':app.storage.user['top_p']/100,'repeat_penalty':app.storage.user['repeat_penalty']/100}
        text.value = ''
        jobStat.addJob(app.storage.browser['id'],app.storage.user['pdf_job'],message,job_type = 'pdf_chat' )
        job = {'token':app.storage.browser['id'],'uuid':app.storage.user['pdf_job']}
        try:
            taskQueue.put(job)
                
        except:
            jobStat.updateStatus(app.storage.browser['id'],app.storage.user['pdf_job'],"failed") 

        timer.activate()
        pdf_messages.refresh()

    def summarize_pdf() -> None:
        statistic.addEvent('pdf_summary')
        assign_uuid_if_missing()
        jobStat.addJob(app.storage.browser['id'],app.storage.user['pdf_job'],"",job_type = 'pdf_summarize' )
        job = {'token':app.storage.browser['id'],'uuid':app.storage.user['pdf_job']}
        try:
            taskQueue.put(job)
                
        except:
            jobStat.updateStatus(app.storage.browser['id'],app.storage.user['pdf_job'],"failed") 

        timer.activate()
        pdf_messages.refresh()

    def handle_upload(event: events.UploadEventArguments):
        assign_uuid_if_missing()
        fileid = app.storage.browser['id']
        with event.content as f:
                
            filepath = f'/tmp/{fileid}/{event.name}'
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file = open(filepath, 'wb')
            for line in f.readlines():
                file.write(line)
            file.close()
        jobStat.addJob(app.storage.browser['id'],app.storage.user['pdf_job'],prompt = '',custom_config = False,job_type = 'pdf_processing' )
        job = {'token':app.storage.browser['id'],'uuid':app.storage.user['pdf_job'],'filepath':filepath}
        try:
            taskQueue.put(job)
            pdf_ready['ready'] = False
            pdf_ready['answered'] = False
        except:
            jobStat.updateStatus(app.storage.browser['id'],app.storage.user['pdf_job'],"failed") 
        pdf_ready['ready_to_upload'] = False
        timer.activate()
        pdf_messages.refresh()

    navigation()
        
        # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
    ui.query('.q-page').classes('flex')
    ui.query('.nicegui-content').classes('w-full')
        
        

    with ui.tabs().classes('w-full') as tabs:
            pdf_tab = ui.tab('PDF')

    with ui.tab_panels(tabs, value=pdf_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        with ui.tab_panel(pdf_tab).classes('items-stretch'):
            pdf_messages()

            ui.upload(on_upload=handle_upload,multiple=True,label='Upload Files',max_total_size=9048576).props('accept=".pdf,.docx,.csv"').classes('max-w-full').bind_visibility_from(pdf_ready,'ready_to_upload')


    with ui.footer().classes('bg-white'):
        with ui.column().classes('w-full max-w-3xl mx-auto my-6'):
                

                
                
            with ui.row().classes('w-full no-wrap items-center').bind_visibility_from(pdf_ready,'ready'):
                placeholder = 'message' 
                text = ui.textarea(placeholder=placeholder).props('rounded outlined input-class=mx-3').props('clearable') \
                .classes('w-full self-center').bind_value(app.storage.user, 'pdf_question').on('keydown.enter', send).bind_visibility_from(pdf_ready,'answered')
                send_btn = ui.button(icon="send", on_click=lambda: send()).bind_visibility_from(pdf_ready,'answered')
                summarize_btn = ui.button("summarize pdf", on_click=lambda: summarize_pdf()).bind_visibility_from(pdf_ready,'answered')
                copy_btn = ui.button(icon="content_copy", on_click=lambda: copy_data())
                delete_btn = ui.button(icon="delete_forever", on_click=lambda: delete_chat())
       