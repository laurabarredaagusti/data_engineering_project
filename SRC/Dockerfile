FROM python:3.7.13-bullseye
WORKDIR app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST 0.0.0.0
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
COPY . . 
EXPOSE 5000
CMD ["python", "app.py"]