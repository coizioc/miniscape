FROM python:3

RUN mkdir -p /opt/miniscape
WORKDIR /opt/miniscape
COPY requirements.txt ./

RUN touch config.py db.sqlite3

RUN pip install --upgrade pip
RUN pip --disable-pip-version-check install --no-cache-dir  -r requirements.txt --root-user-action=ignore
COPY . ./

CMD [ "python", "./launcher.py"]