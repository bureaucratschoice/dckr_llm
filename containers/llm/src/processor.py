import os
import threading  # Import threading for concurrency
from model import ModelHandler
from jobtools import ChatJob, JobRegister, RoleToggle

# Initialize the model handler and load the LLM
model_handler = ModelHandler()
llm = model_handler.build()


class MainProcessor(threading.Thread):
    """
    A thread-based class that processes chat jobs from a task queue using an LLM (Large Language Model). 
    It pulls jobs from the queue, streams responses from the LLM, and updates the job's status and content.
    
    Attributes:
        taskLock (threading.Lock): A lock to ensure thread-safe access to shared resources.
        taskQueue (queue.Queue): The queue holding jobs to be processed.
        jobReg (JobRegister): A registry for managing and retrieving job objects by their UUID.
    """

    def __init__(self, taskLock: threading.Lock, taskQueue: "queue.Queue[str]", jobReg: JobRegister):
        """
        Initializes the MainProcessor thread with a task lock, a task queue, and a job registry.

        Args:
            taskLock (threading.Lock): A lock for synchronizing job-related operations.
            taskQueue (queue.Queue): A queue containing job UUIDs to be processed.
            jobReg (JobRegister): A job registry to manage and retrieve jobs.
        """
        super().__init__()  # Initialize the threading.Thread class
        self.taskLock = taskLock
        self.taskQueue = taskQueue
        self.jobReg = jobReg

    def run(self):
        """
        The main loop of the thread. Continuously pulls jobs from the task queue and processes them.
        For each job, it streams responses from the LLM and updates the job's status and content.
        """
        while True:
            # Retrieve a job UUID from the task queue (blocking call)
            uuid = self.taskQueue.get(block=True)
            
            try:
                # Retrieve the job from the job registry using the UUID
                job = self.jobReg.getJob(uuid)
                job.setStatus("processing")

                # Initialize the message toggle (alternating between 'user' and 'assistant')
                toggle = RoleToggle("user", "assistant")
                messages = [{"role": "system", "content": job.getSysPrompt()}]

                # Append previous messages to the conversation
                for message in job.getMessages():
                    messages.append({"role": toggle.toggle(), "content": message})

                # Stream the response from the LLM
                try:
                    completionStream = llm.create_chat_completion(
                        messages, stream=True
                    )
                    for chunk in completionStream:
                        print(chunk)  # Optional: Replace with logging in production
                        job.appendChunk(chunk)  # Store streamed chunk in the job

                except Exception as e:
                    # Handle LLM errors gracefully by logging and storing an error message
                    print(f"Error during LLM completion: {e}")
                    error_message = os.getenv('CHATERROR', 'An error occurred.')
                    job.appendChunk(error_message)

                # Finalize the job by appending the full message and setting status
                job.appendMessage()  # Verify if parameters are needed
                job.setStatus("finished")

            finally:
                # Mark the task as done to avoid deadlocks
                self.taskQueue.task_done()


# Example usage (assuming taskQueue and jobReg are defined elsewhere):
# taskLock = threading.Lock()
# taskQueue = queue.Queue()
# jobReg = JobRegister()
# processor = MainProcessor(taskLock, taskQueue, jobReg)
# processor.start()
