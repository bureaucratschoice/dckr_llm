import os
import threading  # Import threading for concurrency
from model import ModelHandler
from jobtools import ChatJob, JobRegister, RoleToggle

# Initialize the model handler and load the LLM
model_handler = ModelHandler()
llm = model_handler.build()


class MainProcessor(threading.Thread):
    """
    A thread-based class that processes jobs (ChatJob) from a task queue using an LLM. 
    It pulls jobs from the queue, processes them based on the job type, and updates the job's status and content.
    
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
        For each job, it determines whether it's a ChatJob and processes it accordingly.
        """
        while True:
            # Retrieve a job UUID from the task queue (blocking call)
            uuid = self.taskQueue.get(block=True)

            try:
                # Retrieve the job from the job registry using the UUID
                job = self.jobReg.get_job(uuid)
                
                if isinstance(job, ChatJob):
                    self.process_chat_job(job)
                else:
                    print(f"Unknown job type for UUID: {uuid}")

            finally:
                # Mark the task as done to avoid deadlocks
                self.taskQueue.task_done()

    def process_chat_job(self, job: ChatJob):
        """
        Process a ChatJob by streaming responses from an LLM and updating the job's status and content.

        Args:
            job (ChatJob): The chat job to process.
        """
        try:
            job.set_status("processing")
            toggle = RoleToggle("user", "assistant")
            messages = [{"role": "system", "content": job.get_sys_prompt()}]

            # Append previous messages to the conversation
            for message in job.get_messages():
                messages.append({"role": toggle.toggle(), "content": message})

            try:
                # Stream the response from the LLM
                print(messages)
                completionStream = llm.create_chat_completion(
                    messages, stream=True
                )
                for chunk in completionStream:
                    if chunk.get('choices')[0].get('delta').get('content'):
                        job.append_chunk(chunk.get('choices')[0].get('delta').get('content'))  # Store streamed chunk in the job

            except Exception as e:
                # Handle LLM errors gracefully by logging and storing an error message
                print(f"Error during LLM completion: {e}")
                error_message = os.getenv('CHATERROR', 'An error occurred.')
                job.append_chunk(error_message)

            # Finalize the job by appending the full message and setting status
            job.set_status("finished")
        except Exception as e:
            print(f"Error during ChatJob processing: {e}")
    