import threading
import queue
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter
from typing import Union, Any
from jobtools import VectorJob, JobRegister
import uuid
import numpy as np

class MainProcessor(threading.Thread):
    """
    A background processor thread to handle tasks asynchronously,
    specifically for processing VectorJob instances with QdrantClient.
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

        # Initialize Qdrant client (assuming Qdrant is running locally on default port)
        self.qdrant_client = QdrantClient(url="http://localhost:6333")

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
        # Check if the collection exists, if not, create it
        if not self.qdrant_client.get_collection(collection_name):
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vector_size=512,  # Adjust the vector size based on your embedding model
                distance="Cosine"  # or "Dot" or "Euclidean" based on your needs
            )

        # Generate embeddings for each file and insert as points
        embeddings = self.generate_embeddings(job.get_files())
        points = [
            PointStruct(
                id=str(uuid.uuid4()),  # Generate unique ID for each point
                vector=embedding,
                payload={
                    "source": job.get_metadata().get("source"),
                    "author": job.get_metadata().get("author"),
                    "content": file_content
                }
            ) for embedding, file_content in zip(embeddings, job.get_files())
        ]

        # Upload points to the collection
        self.qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )

        job.set_result({"message": "Files uploaded successfully", "points_count": len(points)})

    def process_query(self, job: VectorJob) -> None:
        """
        Process a query job to retrieve similar vectors from a collection.

        Args:
            job (VectorJob): The vector job for querying the vector store.
        """
        collection_name = job.get_collection()
        query_embedding = self.generate_embedding(job.get_query())

        # Perform the search query in Qdrant
        search_result = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=5,  # Adjust the number of results as needed
            with_payload=True
        )

        # Format results
        result_data = [
            {
                "score": point.score,
                "metadata": point.payload
            } for point in search_result
        ]

        job.set_result(result_data)

    def generate_embeddings(self, texts: list) -> list:
        """
        Generate embeddings for a list of texts. Placeholder for actual embedding generation.

        Args:
            texts (list): A list of text strings.

        Returns:
            list: A list of embeddings.
        """
        # Replace this with your actual embedding generation logic, e.g., using a transformer model.
        return [np.random.rand(512).tolist() for _ in texts]

    def generate_embedding(self, text: str) -> list:
        """
        Generate an embedding for a single text. Placeholder for actual embedding generation.

        Args:
            text (str): A text string.

        Returns:
            list: The generated embedding.
        """
        # Replace this with actual embedding generation logic.
        return np.random.rand(512).tolist()
