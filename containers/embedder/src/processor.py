import os
import threading  # Import threading for concurrency
from model import ModelHandler
from jobtools import EmbedJob, JobRegister

# Initialize the model handler and load the LLM
model_handler = ModelHandler()
llm = model_handler.build()


class MainProcessor(threading.Thread):
    """
    A thread-based class that processes jobs (EmbedJob) from a task queue using an LLM. 
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
        For each job, it determines whether it's an EmbedJob and processes it accordingly.
        """
        while True:
            # Retrieve a job UUID from the task queue (blocking call)
            uuid = self.taskQueue.get(block=True)

            try:
                # Retrieve the job from the job registry using the UUID
                job = self.jobReg.get_job(uuid)
                
            
                if isinstance(job, EmbedJob):
                    self.process_embed_job(job)
                else:
                    print(f"Unknown job type for UUID: {uuid}")

            finally:
                # Mark the task as done to avoid deadlocks
                self.taskQueue.task_done()


    def process_embed_job(self, job: EmbedJob):
        """
        Process an EmbedJob by generating an embedding for the text and updating the job's status.

        Args:
            job (EmbedJob): The embedding job to process.
        """
        job.set_status("processing")

        try:
            # Simulate embedding process (replace with actual embedding logic)
            print(f"Embedding text: {job.get_text()}")
            embedding = self.generate_embedding(job.get_text())
            job.set_embedding(embedding)

        except Exception as e:
            # Handle embedding errors gracefully by logging and storing an error message
            print(f"Error during embedding: {e}")
            job.set_embedding(None)

        # Finalize the job by setting the status to finished
        job.set_status("finished")

    def generate_embedding(self, text: str) -> List[float]:
        """
        A placeholder method for generating embeddings from text. Replace this with actual embedding logic.

        Args:
            text (str): The text to be embedded.

        Returns:
            List[float]: A list of floats representing the embedding.
        """
        # Placeholder: Convert text to a dummy vector (e.g., character ASCII values).
        
        return llm.embed(text)



# Example usage (assuming taskQueue and jobReg are defined elsewhere):
# taskLock = threading.Lock()
# taskQueue = queue.Queue()
# jobReg = JobRegister()
# processor = MainProcessor(taskLock, taskQueue, jobReg)
# processor.start()
