FROM bureaucratschoice/dckr_llm:llm_runtime_0.1

RUN apt-get update
RUN apt-get upgrade

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ADD ./src/ /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"] 

