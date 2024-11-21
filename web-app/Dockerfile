FROM python:3.9

WORKDIR /app

RUN pip install --upgrade pip setuptools pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY . .

CMD ["python", "app.py"]
