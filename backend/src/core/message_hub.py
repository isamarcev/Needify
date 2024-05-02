import json

from aiokafka import AIOKafkaConsumer


class MessageHub:

    def __init__(self, consumer: AIOKafkaConsumer, handlers: dict):
        self.consumer = consumer
        self.handlers = handlers


    async def consume(self):
        await self.consumer.start()
        print("consumer started")
        try:
            async for msg in self.consumer:
                data = json.loads(msg.value)
                print(data)
                handlers_list = self.handlers.get(msg.topic, [])
                print(handlers_list, "handlers_list")
                for handler_class in handlers_list:
                    try:
                        print(handler_class, "HANDLER CLASS")
                        handler = handler_class()
                        print(handler, "HANDLER")
                        data = json.loads(msg.value)
                        print(data, "DATA")
                        await handler(json.loads(msg.value))
                    except Exception as handler_error:
                        print("Error in handler:", handler_error)
                print(
                    "consumed: ",
                    msg.topic,
                )
        except Exception as e:
            # traceback.print_exc()  # Этот метод выводит полный трейсбек ошибки
            print(e, "ERROR in CUNSUME")
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await self.consumer.stop()
