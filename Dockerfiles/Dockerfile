FROM python:3-slim

RUN mkdir /data

WORKDIR /usr/src/status-light

# Install dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Copy the project
COPY ./status-light .

# Start the app 
CMD [ "python", "-u", "./status-light.py" ]
