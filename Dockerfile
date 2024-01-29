FROM python:3.9.13
#EXPOSE 8888
EXPOSE 8051
#EXPOSE 8080
WORKDIR /appcodes_v1
COPY . .
RUN pip install -r requirements.txt
#ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=127.0.0.1"]
#ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=192.168.1.8"]
#ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=127.0.0.1"]
ENTRYPOINT ["streamlit", "run"]
CMD [ "app.py" ]