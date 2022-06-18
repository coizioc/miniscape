FROM python:3

RUN mkdir -p /opt/miniscape
WORKDIR /opt/miniscape
COPY requirements.txt ./

RUN touch config.py db.sqlite3

RUN pip install --no-cache-dir -r requirements.txt
COPY . ./

CMD [ "python", "./launcher.py"]