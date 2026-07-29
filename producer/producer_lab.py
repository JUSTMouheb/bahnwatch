from confluent_kafka import Producer

producer_config = {
    "bootstrap.servers" : "127.0.0.1:9092"
}
producer = Producer(producer_config)
def delivery_report(err,msg):
    if err is not None:
        print("Message delivery failed : {}".format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(),msg.partition()))
topic = "producer-lab"
key1 = "key2"
producer.produce(
    topic=topic,
    key=key1,
    value="message-1",
    partition=2,
    on_delivery=delivery_report,
)
producer.flush()