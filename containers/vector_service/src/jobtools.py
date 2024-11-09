from uuid import uuid4
from typing import List, Dict, Optional, Union


class VectorJob:
    """
    A class to manage vector-related tasks, such as uploading files with metadata or querying a vector store.

    Attributes:
        files (Optional[List[str]]): The list of file contents to be uploaded.
        metadata (Optional[Dict[str, str]]): Metadata associated with the files (e.g., source, author).
        query (Optional[str]): The query string for searching the vector store.
        collection (str): The name of the vector store collection.
        task_type (str): The type of task ('upload' or 'query').
        uuid (str): A unique identifier for the vector job.
        status (str): The current status of the vector job (e.g., 'created', 'processing', 'completed').
        result (Optional[Union[Dict, List[float]]]): The result of the task, such as query results or confirmation of upload.
    """

    def __init__(self, files: Optional[List[str]] = None, metadata: Optional[Dict[str, str]] = None,
                 query: Optional[str] = None, collection: str = "", task_type: str = "upload"):
        """
        Initializes a VectorJob instance for either file upload or query.

        Args:
            files (Optional[List[str]]): List of file contents to upload.
            metadata (Optional[Dict[str, str]]): Metadata for the files.
            query (Optional[str]): Query string for searching.
            collection (str): The vector store collection name.
            task_type (str): The task type, either 'upload' or 'query'.
        """
        self.files = files
        self.metadata = metadata
        self.query = query
        self.collection = collection
        self.task_type = task_type
        self.uuid = str(uuid4().hex)
        self.status = "created"
        self.result: Optional[Union[Dict, List[float]]] = None

    def set_result(self, result: Union[Dict, List[float]]) -> None:
        """
        Sets the result for the job.

        Args:
            result (Union[Dict, List[float]]): The result of the job, such as query results or upload confirmation.
        """
        self.result = result

    def get_result(self) -> Optional[Union[Dict, List[float]]]:
        """
        Retrieves the result of the job.

        Returns:
            Optional[Union[Dict, List[float]]]: The result of the job, or None if not yet set.
        """
        return self.result

    def get_files(self) -> Optional[List[str]]:
        """
        Retrieves the files to be uploaded.

        Returns:
            Optional[List[str]]: The list of files, or None if this is a query task.
        """
        return self.files

    def get_metadata(self) -> Optional[Dict[str, str]]:
        """
        Retrieves the metadata for the files.

        Returns:
            Optional[Dict[str, str]]: Metadata dictionary, or None if not provided.
        """
        return self.metadata

    def get_query(self) -> Optional[str]:
        """
        Retrieves the query string.

        Returns:
            Optional[str]: The query string, or None if this is an upload task.
        """
        return self.query

    def get_collection(self) -> str:
        """
        Retrieves the vector store collection name.

        Returns:
            str: The name of the collection.
        """
        return self.collection

    def get_task_type(self) -> str:
        """
        Retrieves the task type (either 'upload' or 'query').

        Returns:
            str: The task type.
        """
        return self.task_type

    def get_uuid(self) -> str:
        """
        Retrieves the unique identifier of the vector job.

        Returns:
            str: The UUID of the vector job.
        """
        return self.uuid

    def get_status(self) -> str:
        """
        Retrieves the current status of the vector job.

        Returns:
            str: The status of the job.
        """
        return self.status

    def set_status(self, status: str) -> None:
        """
        Updates the status of the vector job.

        Args:
            status (str): The new status to assign to the job.
        """
        self.status = status

class JobRegister:
    """
    A thread-safe class to manage the registration and tracking of multiple jobs.

    Attributes:
        register (Dict[str, VectorJob]): A dictionary storing jobs by their UUID.
        lock (RLock): A reentrant lock to ensure thread-safe operations.
    """

    def __init__(self):
        """
        Initializes a JobRegister instance with an empty register and a lock.
        """
        self.register: Dict[str, VectorJob] = {}
        self.lock = RLock()

    def delete_job(self, uuid: str) -> None:
        """
        Deletes a job from the register by its UUID.

        Args:
            uuid (str): The UUID of the job to delete.

        Raises:
            KeyError: If the UUID is not found in the register.
        """
        with self.lock:
            try:
                del self.register[uuid]
            except Exception as e:
                print(e)

    def add_job(self, job: VectorJob) -> None:
        """
        Adds a job to the register.

        Args:
            job (VectorJob): The job instance to add.
        """
        with self.lock:
            self.register[job.get_uuid()] = job

    def get_job(self, uuid: str) -> Optional[VectorJob]:
        """
        Retrieves a job from the register by its UUID.

        Args:
            uuid (str): The UUID of the job to retrieve.

        Returns:
            Optional[VectorJob]: The job instance if found, otherwise None.
        """
        with self.lock:
            return self.register.get(uuid)