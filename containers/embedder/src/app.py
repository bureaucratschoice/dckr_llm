import os
import threading
import queue
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List

from processor import MainProcessor
from jobtools import EmbedJob, JobRegister

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


class EmbedRequest(BaseModel):
    text: str

@app.post("/getStatus/")
async def get_status(info: InfoRequest) -> Any:
    """
    Get the status of a job based on its UUID.

    Args:
        info (InfoRequest): The request containing the UUID of the job.

    Returns:
        Any: The status of the job.
    """
    return {"status":jobReg.get_job(info.uuid).get_status(),"queue_size":taskQueue.qsize()}


@app.post("/getCompletion/")
async def get_completion(info: InfoRequest) -> Any:
    """
    Get the completion or embedding and status of a job based on its UUID.

    Args:
        info (InfoRequest): The request containing the UUID of the job.

    Returns:
        dict: A dictionary containing the job's completion/embedding and status.
    """
    job = jobReg.get_job(info.uuid)
    if job:

       
        # Check if it's an EmbedJob and return the embedding
        if isinstance(job, EmbedJob):
            return {
                "embedding": job.get_embedding(),
                "status": job.get_status()
            }
        else:
            return {
                "error": "Unknown job type",
                "status": job.get_status()
            }
    else:
        return {
            "error": "Job not found",
            "completion": "",
            "embedding": "",
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



@app.post("/embed/")
async def embed_job(item: EmbedRequest) -> Any:
    """
    Create an embed job for the given text and add it to the job queue.

    Args:
        item (EmbedRequest): The request containing the text to be embedded.

    Returns:
        dict: The UUID and status of the created job.
    """
    job = EmbedJob(item.text)
    jobReg.add_job(job)
    
    try:
        taskQueue.put(job.get_uuid())
    except queue.Full:
        job.set_status("failed")

    return {
        "uuid": job.get_uuid(),
        "status": job.get_status()
    }