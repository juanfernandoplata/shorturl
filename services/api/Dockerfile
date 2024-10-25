FROM python-grpc

WORKDIR /root

COPY ./src/ .

RUN python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /root/_base62

RUN python setup.py build && python setup.py install

WORKDIR /root

CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "80", "main:app" ]