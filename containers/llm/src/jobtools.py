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
        self.uuid = uuid4().hex
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

class JobRegister:
    """
    A thread-safe class to manage the registration and tracking of multiple jobs.

    Attributes:
        register (Dict[str, ChatJob]): A dictionary storing jobs by their UUID.
        lock (RLock): A reentrant lock to ensure thread-safe operations.
    """

    def __init__(self):
        """
        Initializes a JobRegister instance with an empty register and a lock.
        """
        self.register: Dict[str, 'ChatJob'] = {}
        self.lock = RLock()  # Reentrant lock for thread safety.

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
            except KeyError:
                raise KeyError(f"Job with UUID '{uuid}' does not exist.")

    def add_job(self, job: 'ChatJob') -> None:
        """
        Adds a job to the register.

        Args:
            job (ChatJob): The job instance to add.
        """
        with self.lock:
            self.register[job.get_uuid()] = job

    def get_job(self, uuid: str) -> Optional['ChatJob']:
        """
        Retrieves a job from the register by its UUID.

        Args:
            uuid (str): The UUID of the job to retrieve.

        Returns:
            Optional[ChatJob]: The job instance if found, otherwise None.
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
