FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make \
    libopenblas-dev liblapack-dev gfortran \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install prophet cmdstanpy

# Install CmdStan (backend for Prophet)
RUN python -c "import cmdstanpy; cmdstanpy.install_cmdstan()"

COPY . .

EXPOSE 8501
CMD streamlit run apps/web/Home.py --server.port=${PORT:-8501} --server.address=0.0.0.0