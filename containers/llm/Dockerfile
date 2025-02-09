FROM bureaucratschoice/dckr_llm_runtime:0.1
#FROM bureaucratschoice/docker_llm_runtime_arm64:0.1.2

RUN apt-get update 
RUN apt-get upgrade -y

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ADD ./src/ /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"] 

