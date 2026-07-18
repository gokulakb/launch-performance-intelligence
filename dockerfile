FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install setuptools==69.0.3 && \
    pip install -r requirements.txt

COPY . .

RUN python render_init.py

CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
