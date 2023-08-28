# Use the python official image
FROM python:3

EXPOSE 5010

# Set the working directory
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src  /usr/src/app/src

CMD [ "python", "./src/FrontEnd.py" ]
