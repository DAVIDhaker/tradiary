FROM python:3.8

WORKDIR /app/

COPY app /app/app/
COPY app_invest /app/app_invest/
COPY app_trade /app/app_trade/
COPY static /app/static/
COPY templates /app/templates/
COPY fixtures /app/fixtures/
COPY manage.py /app/

RUN pip install django==3.2.7
RUN pip install python-dotenv

EXPOSE 8000

CMD ["/app/manage.py", "runserver", "0.0.0.0:8000"]