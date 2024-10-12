
import requests
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, List
from uuid import uuid4

from model import ModelHandler
from processor import MainProcessor
from jobtools import ChatJob, JobRegister, RoleToggle 

model_handler = ModelHandler()
llm = model_handler.build()



supertoken = os.getenv('SUPERTOKEN',default="PLEASE_CHANGE_THIS_PLEASE")


jobReg = JobRegister()

taskLock = threading.Lock()
taskQueue = queue.Queue(1000)

thread = MainProcessor(taskLock,taskQueue,jobReg)
thread.start()

app = FastAPI()


class Conversation(BaseModel):
    messages: List[str]

class Status(BaseModel):
    uuid: str



@app.post("/getStatus/")
async def get_status(status: Status) -> Any:
    return jobReg.get_job(uuid)

@app.post("/chat/")
async def chat(item: Conversation) -> Any:
    uuid = uuid4().hex
    
    jobStat.addJob(item.token,uuid,item.prompt) 
        job = {'token':item.token,'uuid':uuid}
        try:
            taskQueue.put(job)
        except:
            jobStat.updateStatus(item.token,uuid,"failed")
        result = jobStat.getJobStatus(item.token,uuid)
    else:
        result = "Access denied."
    return result
