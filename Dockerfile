FROM python:3

EXPOSE 3200

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

COPY . /app
RUN pip3 install gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:3200", "app:api"]
