import os
import threading
import queue
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import Any, List, Optional
from processor import MainProcessor
from jobtools import JobRegister, VectorJob
from datetime import date

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

# Define models for metadata and request structures
class FileMetadata(BaseModel):
    source: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    date: Optional[date] = None

class QueryRequest(BaseModel):
    query: str
    collection: str
    metadata: Optional[FileMetadata] = None

class InfoRequest(BaseModel):
    uuid: str

@app.post("/uploadFiles/")
async def upload_files(
    files: List[UploadFile] = File(...),
    metadata: str = Form(...),  # Expect metadata as JSON string
    collection: str = Form(...)
) -> Any:
    """
    Upload a list of files to a vector store collection.

    Args:
        files (List[UploadFile]): List of uploaded files.
        metadata (str): JSON string of metadata information.
        collection (str): Name of the vector collection.

    Returns:
        dict: The UUID of the created job.
    """
    # Parse the metadata JSON string
    try:
        metadata_obj = FileMetadata.parse_raw(metadata)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid metadata format")

    if jobReg.collection_exists(collection):
        raise HTTPException(status_code=400, detail="Collection already exists.")

    # Process file contents as bytes
    file_contents = [await file.read() for file in files]

    job = VectorJob(
        files=file_contents,
        metadata=metadata_obj.dict(),
        collection=collection,
        task_type="upload"
    )
    jobReg.add_job(job)

    try:
        taskQueue.put(job.get_uuid())
    except queue.Full:
        job.set_status("failed")
    
    return {"uuid": job.get_uuid(), "status": job.get_status()}


@app.post("/queryVectorStore/")
async def query_vector_store(request: QueryRequest) -> Any:
    """
    Retrieve text and metadata from a vector store based on a query and collection.

    Args:
        request (QueryRequest): Contains the query string and collection name.

    Returns:
        dict: The UUID of the created job.
    """
    if not jobReg.collection_exists(request.collection):
        return HTTPException(status_code=404, detail="Collection not found.")
    
    job = VectorJob(
        query=request.query,
        collection=request.collection,
        task_type="query"
    )
    jobReg.add_job(job)

    try:
        taskQueue.put(job.get_uuid())
    except queue.Full:
        job.set_status("failed")
    
    return {"uuid": job.get_uuid(), "status": job.get_status()}


@app.post("/getStatus/")
async def get_status(info: InfoRequest) -> Any:
    """
    Get the status of a job based on its UUID.

    Args:
        info (InfoRequest): The request containing the UUID of the job.

    Returns:
        Any: The status of the job.
    """
    return {"status": jobReg.get_job(info.uuid).get_status(), "queue_size": taskQueue.qsize()}


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
        if isinstance(job, VectorJob) and job.task_type == "query":
            return {
                "result": job.get_result(),  # Assumes result is stored after processing
                "status": job.get_status()
            }
        else:
            return {"error": "Unknown job type", "status": job.get_status()}
    else:
        return {"error": "Job not found", "status": ""}


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
