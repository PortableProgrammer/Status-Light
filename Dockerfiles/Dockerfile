FROM python:3-alpine

WORKDIR /usr/src/status-light

# Install dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY ./status-light .

# Start the app 
CMD [ "python", "./status-light.py" ]