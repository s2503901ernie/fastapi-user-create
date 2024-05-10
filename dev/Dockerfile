FROM python:3.11-slim
WORKDIR /root/api-service
COPY ./requirements.txt /root/api-service
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./src /root/api-service
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
