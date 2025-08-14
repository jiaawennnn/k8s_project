FROM python:3.10.10

WORKDIR /training

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .  .

EXPOSE 5002

CMD ["python", "train.py"]