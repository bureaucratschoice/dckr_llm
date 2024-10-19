import requests
from typing import List, Dict, Any

class ChatClient:
    """
    A client to interact with the FastAPI chat application, providing methods
    to send chat requests and retrieve job completions.
    """

    def __init__(self, base_url: str = "http://llm:80"):
        """
        Initialize the ChatClient with the base URL of the FastAPI service.

        Args:
            base_url (str): Base URL of the FastAPI app.
        """
        self.base_url = base_url

    def send_chat(self, sysprompt: str, messages: List[str]) -> str:
        """
        Sends a chat request to the /chat/ endpoint.

        Args:
            sysprompt (str): System prompt for the chat.
            messages (List[str]): List of user messages.

        Returns:
            str: UUID of the created job or error message if request fails.
        """
        url = f"{self.base_url}/chat/"
        payload = {"sysprompt": sysprompt, "messages": messages}
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()  # Return the job's UUID
        except requests.exceptions.RequestException as e:
            return f"Chat request failed: {e}"

    def get_completion(self, uuid: str) -> Dict[str, Any]:
        """
        Retrieves the completion and status of a job based on its UUID.

        Args:
            uuid (str): UUID of the job.

        Returns:
            dict: A dictionary containing the job's completion and status,
                  or an error message if the request fails.
        """
        url = f"{self.base_url}/getCompletion/"
        payload = {"uuid": uuid}
        

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()  # Return job's status and completion
        except requests.exceptions.RequestException as e:
            return {"error": f"Completion request failed: {e}"}

    def unregister_job(self, uuid: str) -> str:
        """
        Unregisters a job using its UUID by calling the /unregisterJob/ endpoint.

        Args:
            uuid (str): UUID of the job to be unregistered.

        Returns:
            str: A confirmation message or an error message if the request fails.
        """
        url = f"{self.base_url}/unregisterJob/"
        payload = {"uuid": uuid}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.text  # Should return "OK" on success
        except requests.exceptions.RequestException as e:
            return f"Unregister job request failed: {e}"