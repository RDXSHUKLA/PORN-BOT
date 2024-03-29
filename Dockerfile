FROM python:3.10.6

WORKDIR /app
COPY . /app/

# Install required dependencies, upgrade pip, and install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["bash", "run.sh"]
