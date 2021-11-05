FROM python:3

#ENV postcode='postcode'
ENV station='station'
ENV useMQTT='FALSE'
ENV mqttBroker = 'brokerAddress'
ENV mqttUser='mqttUser'
ENV mqttPass='mqttPass'
ENV mqttBase='mqttBase'

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./refactored.py"]