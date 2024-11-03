from uuid import uuid4
from typing import List, Dict, Optional
from threading import RLock

class ChatJob:
    """
    A class to manage chat interactions, including system prompts, messages, and completion status.

    Attributes:
        sys_prompt (str): The system prompt to guide chat interactions.
        messages (List[str]): A list of chat messages exchanged during the interaction.
        uuid (str): A unique identifier for the chat job.
        status (str): The current status of the chat job.
        completion (str): The ongoing or accumulated completion text.
    """

    def __init__(self, sys_prompt: str, messages: List[str]):
        """
        Initializes a ChatJob instance with a system prompt and messages.

        Args:
            sys_prompt (str): The system prompt guiding the chat.
            messages (List[str]): Initial chat messages.
        """
        self.sys_prompt = sys_prompt
        self.messages = messages
        self.uuid = str(uuid4().hex)
        self.status = "created"
        self.completion = ""

    def append_chunk(self, chunk: str) -> None:
        """
        Appends a chunk of text to the current completion.

        Args:
            chunk (str): A string chunk to add to the completion.
        """
        self.completion += chunk

    def append_message(self) -> None:
        """
        Appends the current completion to the list of messages and resets the completion text.
        """
        self.messages.append(self.completion)
        self.completion = ""

    def get_completion(self) -> str:
        """
        Retrieves the completion.

        Returns:
            str: The completion.
        """
        return self.completion
        
    def get_messages(self) -> List[str]:
        """
        Retrieves the list of chat messages.

        Returns:
            List[str]: A list of messages.
        """
        return self.messages

    def get_status(self) -> str:
        """
        Retrieves the current status of the chat job.

        Returns:
            str: The status of the chat job.
        """
        return self.status

    def get_sys_prompt(self) -> str:
        """
        Retrieves the system prompt.

        Returns:
            str: The system prompt for the chat job.
        """
        return self.sys_prompt

    def get_uuid(self) -> str:
        """
        Retrieves the unique identifier of the chat job.

        Returns:
            str: The UUID of the chat job.
        """
        return self.uuid

    def set_status(self, status: str) -> None:
        """
        Updates the status of the chat job.

        Args:
            status (str): The new status to assign to the chat job.
        """
        self.status = status

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
        register (Dict[str, Union[ChatJob, EmbedJob]]): A dictionary storing jobs by their UUID.
        lock (RLock): A reentrant lock to ensure thread-safe operations.
    """

    def __init__(self):
        """
        Initializes a JobRegister instance with an empty register and a lock.
        """
        self.register: Dict[str, Union[ChatJob, EmbedJob]] = {}
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

    def add_job(self, job: Union[ChatJob, EmbedJob]) -> None:
        """
        Adds a job to the register.

        Args:
            job (ChatJob | EmbedJob): The job instance to add.
        """
        with self.lock:
            self.register[job.get_uuid()] = job

    def get_job(self, uuid: str) -> Optional[Union[ChatJob, EmbedJob]]:
        """
        Retrieves a job from the register by its UUID.

        Args:
            uuid (str): The UUID of the job to retrieve.

        Returns:
            Optional[ChatJob | EmbedJob]: The job instance if found, otherwise None.
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
