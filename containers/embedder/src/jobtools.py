from uuid import uuid4
from typing import List, Dict, Optional
from threading import RLock


class EmbedJob:
    """
    A class to manage embedding tasks, including the input text, embedding result, and job status.

    Attributes:
        text (str): The text string to be embedded.
        uuid (str): A unique identifier for the embed job.
        status (str): The current status of the embed job (e.g., 'created', 'processing', 'completed').
        embedding (Optional[List[float]]): The embedded vector, if available.
    """

    def __init__(self, text: str):
        """
        Initializes an EmbedJob instance with the text string.

        Args:
            text (str): The text to be embedded.
        """
        self.text = text
        self.uuid = str(uuid4().hex)
        self.status = "created"
        self.embedding: Optional[List[float]] = None

    def set_embedding(self, embedding: List[float]) -> None:
        """
        Sets the embedding for the job.

        Args:
            embedding (List[float]): The embedded vector to assign to the job.
        """
        self.embedding = embedding

    def get_embedding(self) -> Optional[List[float]]:
        """
        Retrieves the embedding result.

        Returns:
            Optional[List[float]]: The embedded vector, or None if not yet set.
        """
        return self.embedding

    def get_text(self) -> str:
        """
        Retrieves the original text string.

        Returns:
            str: The text string to be embedded.
        """
        return self.text

    def get_status(self) -> str:
        """
        Retrieves the current status of the embed job.

        Returns:
            str: The status of the embed job.
        """
        return self.status

    def get_uuid(self) -> str:
        """
        Retrieves the unique identifier of the embed job.

        Returns:
            str: The UUID of the embed job.
        """
        return self.uuid

    def set_status(self, status: str) -> None:
        """
        Updates the status of the embed job.

        Args:
            status (str): The new status to assign to the embed job.
        """
        self.status = status

class JobRegister:
    """
    A thread-safe class to manage the registration and tracking of multiple jobs.

    Attributes:
        register (Dict[str, EmbedJob]): A dictionary storing jobs by their UUID.
        lock (RLock): A reentrant lock to ensure thread-safe operations.
    """

    def __init__(self):
        """
        Initializes a JobRegister instance with an empty register and a lock.
        """
        self.register: Dict[str, EmbedJob] = {}
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

    def add_job(self, job: EmbedJob) -> None:
        """
        Adds a job to the register.

        Args:
            job (EmbedJob): The job instance to add.
        """
        with self.lock:
            self.register[job.get_uuid()] = job

    def get_job(self, uuid: str) -> Optional[EmbedJob]:
        """
        Retrieves a job from the register by its UUID.

        Args:
            uuid (str): The UUID of the job to retrieve.

        Returns:
            Optional[EmbedJob]: The job instance if found, otherwise None.
        """
        with self.lock:
            return self.register.get(uuid)

class RoleToggle:
    """
    A class to toggle between two roles: 'user' and 'assistant'.

    Attributes:
    -----------
    user : str
        Represents the user role.
    assistant : str
        Represents the assistant role.
    _acting : str
        The role currently acting (either 'user' or 'assistant').

    Methods:
    --------
    toggle() -> str:
        Toggles between the 'user' and 'assistant' roles, returning the 
        role that was active before the switch.
    """

    def __init__(self, user: str, assistant: str):
        """
        Initializes the RoleToggle class with user and assistant roles.

        Parameters:
        -----------
        user : str
            The user role.
        assistant : str
            The assistant role.
        """
        self.user = user
        self.assistant = assistant
        self._acting = self.user  # Start with the user role.

    def toggle(self) -> str:
        """
        Toggles the current role between 'user' and 'assistant'.

        Returns:
        --------
        str
            The role that was active before the toggle.
        """
        previous_role = self._acting
        self._acting = self.assistant if self._acting == self.user else self.user
        return previous_role
