import threading
import queue
import uuid
from qdrant_client import QdrantClient
from typing import Any
from jobtools import VectorJob, JobRegister

class MainProcessor(threading.Thread):
    """
    A background processor thread to handle tasks asynchronously,
    specifically for processing VectorJob instances with QdrantClient and FastEmbed.
    """

    def __init__(self, task_lock: threading.Lock, task_queue: queue.Queue, job_register: JobRegister):
        """
        Initializes the MainProcessor with necessary components.

        Args:
            task_lock (threading.Lock): A lock for synchronizing task access.
            task_queue (queue.Queue): The task queue.
            job_register (JobRegister): Register for managing jobs.
        """
        super(MainProcessor, self).__init__()
        self.task_lock = task_lock
        self.task_queue = task_queue
        self.job_register = job_register

        # Initialize Qdrant client with FastEmbed
        self.qdrant_client = QdrantClient("localhost", port=6333)

    def run(self):
        """
        The main loop to process tasks from the task queue.
        """
        while True:
            job_uuid = self.task_queue.get()  # Block until a job is available
            job = self.job_register.get_job(job_uuid)
            if isinstance(job, VectorJob):
                job.set_status("processing")
                if job.get_task_type() == "upload":
                    self.process_upload(job)
                elif job.get_task_type() == "query":
                    self.process_query(job)
                job.set_status("completed")
            self.task_queue.task_done()

    def process_upload(self, job: VectorJob) -> None:
        """
        Process an upload job to add files to a vector collection.

        Args:
            job (VectorJob): The vector job for uploading files and metadata.
        """
        collection_name = job.get_collection()

        # Check if the collection exists; create if it does not
        if not self.qdrant_client.get_collection(collection_name):
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vector_size=384,  # Adjust vector size if changing the model
                distance="Cosine"  # Default distance metric
            )

        # Retrieve documents as byte content and metadata
        documents = job.get_files()  # List of binary content (bytes)
        decoded_documents = [content.decode("utf-8", errors="ignore") for content in documents]  # Decode bytes to text
        metadata = [
            {
                "source": job.get_metadata().get("source"),
                "author": job.get_metadata().get("author")
            } for _ in documents
        ]
        ids = [str(uuid.uuid4()) for _ in documents]  # Unique IDs for each document

        # Use Qdrant's `add` method to handle embedding and storage
        self.qdrant_client.add(
            collection_name=collection_name,
            documents=decoded_documents,
            metadata=metadata,
            ids=ids
        )

        job.set_result({"message": "Files uploaded successfully", "points_count": len(documents)})

    def process_query(self, job: VectorJob) -> None:
        """
        Process a query job to retrieve similar vectors from a collection.

        Args:
            job (VectorJob): The vector job for querying the vector store.
        """
        collection_name = job.get_collection()
        query_text = job.get_query()

        # Perform the search query using Qdrant's `query` method
        search_result = self.qdrant_client.query(
            collection_name=collection_name,
            query_text=query_text,
            limit=5,  # Number of results to retrieve
            with_payload=True
        )

        # Format the search results
        result_data = [
            {
                "score": point.score,
                "metadata": point.payload
            } for point in search_result
        ]

        job.set_result(result_data)
