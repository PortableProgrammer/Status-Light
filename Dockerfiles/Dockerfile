FROM python:3-slim

RUN mkdir /data

WORKDIR /usr/src/status-light

# Install dependencies
COPY ./requirements.txt ./
RUN apt-get update \
    && apt-get install -y gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc libffi-dev

# Copy the project
COPY ./status-light .

# Start the app 
CMD [ "python", "-u", "./status-light.py" ]
