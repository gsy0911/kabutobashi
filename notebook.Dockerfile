FROM python:3.9-buster

WORKDIR /opt/app

COPY requirements.txt /opt/app
COPY requirements.notebook.txt /opt/app
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements.notebook.txt

COPY kabutobashi /opt/app/src


CMD ["jupyter", "lab"]
