FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Utiliza un comando que mantenga el contenedor en ejecución
CMD ["python", "app.py"]

