from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from .logger import logger

def create_kafka_topics():
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers='kafka:9092',
        )

        topics = [
            NewTopic(
                name="polygon_check_request",
                num_partitions=1,
                replication_factor=1,
            ),
            NewTopic(
                name="polygon_check_result",
                num_partitions=1,
                replication_factor=1,
            ),
        ]

        admin_client.create_topics(new_topics=topics, validate_only=False)
        logger.info("Kafka топики созданы успешно.")
    except TopicAlreadyExistsError:
        logger.info("Kafka топики уже существуют.")
    except Exception as e:
        logger.error(f"Ошибка при создании Kafka топиков: {e}")