import os
import requests
import multiprocessing
from llama_cpp import Llama

class ModelHandler:
    """
    A class to handle downloading and building the Llama model.

    This class manages the lifecycle of a Llama model by:
    1. Downloading the model if it is not found locally.
    2. Initializing the model with parameters specified via environment variables.

    Attributes:
    -----------
    url : str
        The URL from which to download the model if needed.
    filename : str
        The path where the model binary should be saved/loaded from.
    gpu_layers : int
        The number of GPU layers to use for inference.
    verbose : bool
        Controls whether verbose output is enabled during initialization.

    Methods:
    --------
    download_file() -> str:
        Downloads the model from the specified URL and saves it locally.
    
    build() -> Llama:
        Initializes and returns the Llama model instance.
    """

    CHUNK_SIZE = 8192  # Constant for download chunk size

    def __init__(self):
        """
        Initializes the ModelHandler with parameters from environment variables.

        Raises:
        -------
        ValueError:
            If the required environment variables are not set.
        """
        self.url = os.getenv('MODEL_DOWNLOAD_URL')
        self.filename = os.getenv('MODEL_BIN_PATH')
        self.gpu_layers = int(os.getenv('GPU_LAYERS', '0'))  # Default to 0 GPU layers
        self.verbose = True  # Always use verbose mode (non-verbose leads to errors)

        if not self.url or not self.filename:
            raise ValueError("MODEL_DOWNLOAD_URL and MODEL_BIN_PATH must be set.")

    def download_file(self) -> str:
        """
        Downloads the model from the specified URL and saves it locally.

        Returns:
        --------
        str
            The path to the downloaded model file.

        Raises:
        -------
        requests.exceptions.HTTPError:
            If the download request fails with an HTTP error.
        IOError:
            If there is an error writing to the file.
        """
        print(f"Downloading model from {self.url}...")
        with requests.get(self.url, stream=True) as response:
            response.raise_for_status()  # Ensure the request was successful
            with open(self.filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:  # Avoid writing keep-alive chunks
                        f.write(chunk)
        print("Download complete.")
        return self.filename

    def build(self) -> Llama:
        """
        Builds and returns an instance of the Llama model.

        If the model binary is not found locally, it will be downloaded first.

        Returns:
        --------
        Llama
            An initialized Llama model instance.

        Raises:
        -------
        Exception:
            If the Llama model initialization fails.
        """
        if not os.path.exists(self.filename):
            print("Specified model not found. Downloading...")
            self.download_file()

        try:
            print("Initializing Llama model...")
            llm = Llama(
                model_path=self.filename,
                verbose=self.verbose,
                n_ctx=0,
                n_gpu_layers=self.gpu_layers,
                n_threads=multiprocessing.cpu_count(),
                n_threads_batch=multiprocessing.cpu_count()
            )
        except Exception as e:
            print(f"Warning: {e}. Retrying without batch threading...")
            llm = Llama(
                model_path=self.filename,
                verbose=self.verbose,
                n_gpu_layers=self.gpu_layers
            )

        print("Llama model initialized successfully.")
        return llm
