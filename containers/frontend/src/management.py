from navigation import navigation 

def mngmt():
        navigation()
        title = os.getenv('APP_TITLE',default=cfg.get_config('frontend','app_title',default="MWICHT"))
        
        
        def handle_upload(event: events.UploadEventArguments):
            assign_uuid_if_missing()
            fileid = app.storage.browser['id']
            with event.content as f:
                
                filepath = f'/app/static/{event.name}'
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file = open(filepath, 'wb')
                for line in f.readlines():
                    file.write(line)
                file.close()
        ui.button(on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login')), icon='logout').props('outline round')
        ui.markdown('You can upload **.jpeg** files here to customize the appearance of the application.')
        ui.markdown('For the **logo** rename your upload logo.jpeg.')
        ui.markdown('For the **background** images rename your upload home_background[1-4].jpeg')
        ui.upload(on_upload=handle_upload,multiple=False,label='Upload JPEG',max_file_size=9048576).props('accept=.jpeg').classes('max-w-full')