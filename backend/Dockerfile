# Use an official Python 3.12.1 runtime as a base image
FROM python:3.12.1

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y default-libmysqlclient-dev gcc

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python3", "merch.py"]

