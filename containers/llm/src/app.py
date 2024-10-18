import os
import threading
import queue
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, List

from processor import MainProcessor
from jobtools import ChatJob, JobRegister

# Fetch the supertoken from environment variables
supertoken = os.getenv('SUPERTOKEN', default="PLEASE_CHANGE_THIS_PLEASE")

# Initialize job registration and threading components
jobReg = JobRegister()
taskLock = threading.Lock()
taskQueue = queue.Queue(maxsize=1000)

# Start the main processor thread
thread = MainProcessor(taskLock, taskQueue, jobReg)
thread.start()

# Initialize FastAPI app
app = FastAPI()


class Chat(BaseModel):
    sysprompt: str
    messages: List[str]


class InfoRequest(BaseModel):
    uuid: str


@app.post("/getStatus/")
async def get_status(info: InfoRequest) -> Any:
    """
    Get the status of a job based on its UUID.

    Args:
        info (InfoRequest): The request containing the UUID of the job.

    Returns:
        Any: The status of the job.
    """
    return {"message":jobReg.get_job(info.uuid).get_status()}


@app.post("/getCompletion/")
async def get_completion(info: InfoRequest) -> Any:
    """
    Get the completion and status of a job based on its UUID.

    Args:
        info (InfoRequest): The request containing the UUID of the job.

    Returns:
        dict: A dictionary containing the job's completion and status.
    """
    job = jobReg.get_job(info.uuid)
    if job:
        return {
        "completion": job.get_completion(),
        "status": job.get_status()
        }
    else:
        return {
        "completion": "",
        "status": ""
        }


@app.post("/unregisterJob/")
async def unregister_job(info: InfoRequest) -> Any:
    """
    Unregister a job using its UUID.

    Args:
        info (InfoRequest): The request containing the UUID of the job.

    Returns:
        str: A confirmation message.
    """
    jobReg.delete_job(info.uuid)
    return "OK"


@app.post("/chat/")
async def chat(item: Chat) -> Any:
    """
    Process a chat request and add it to the job queue.

    Args:
        item (Chat): The chat request containing the system prompt and messages.

    Returns:
        str: The UUID of the created job.
    """
    job = ChatJob(item.sysprompt, item.messages)
    jobReg.add_job(job)
    try:
        taskQueue.put(job.get_uuid())
    except queue.Full:
        job.set_status("failed")
    return job.get_uuid()
