##################################
# Dockerfile for jlnetosci/astra #
##################################

FROM python:3.11.4-slim-bookworm
LABEL maintainer="João L. Neto (https://github.com/jlnetosci/)"

COPY /app/ /app/
WORKDIR /app/
RUN apt-get update; apt-get install -y wget; apt-get clean; \
pip install streamlit==1.27.1 python-gedcom==1.0.0 pyvis==0.3.2; \
chmod +x app.py; \
apt-get -y autoclean && apt-get -y autoremove

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]