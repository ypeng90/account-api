from datetime import datetime
from esdbclient import ESDBClient, NewEvent
from django.conf import settings
import pickle
import json
from pymongo import MongoClient
from threading import Thread
from uuid import uuid4, UUID

# TODO: fix exceptions.DiscoveryFailed and use secure cluster instead of insecure single server.
#       Failed to read from gossip seed: ['esdb.node1:2111', 'esdb.node2:2112', 'esdb.node3:2113']
# ESDB_SERVERS = [
#     "esdb.node1:2111",
#     "esdb.node2:2112",
#     "esdb.node3:2113",
# ]
# EVENTSTOREDB_URI = f"esdb://{','.join(ESDB_SERVERS)}?TlsVerifyCert=false"
EVENTSTOREDB_URI = "esdb://esdb:2113?Tls=false"


class ESClient(ESDBClient):
    # Does not have __enter__ so that it can not be used as a context manager.
    def __init__(self, stream, type="", data=None):
        super().__init__(uri=EVENTSTOREDB_URI)

        if stream == "user":
            self.stream_name = "user-f64300a8-9ae8-4d33-9b65-853bf58d7e9f"
        elif stream == "token":
            self.stream_name = "token-72523e70-4b0f-489a-8f13-e08cbb176dff"

        if type and data:
            self.event = NewEvent(type=type, data=bytes(data, encoding="utf-8"))
        else:
            self.event = None

    def send(self):
        assert self.event is not None

        expected_position = self.get_stream_position(stream_name=self.stream_name)
        commit_position = self.append_events(
            stream_name=self.stream_name,
            expected_position=expected_position,
            events=[self.event],
        )

        return commit_position

    def receive(self, stream_position):
        recorded = self.read_stream_events(
            stream_name=self.stream_name, stream_position=stream_position
        )

        return recorded

    def subscribe(self, stream_position):
        subscription = self.subscribe_stream_events(
            stream_name=self.stream_name, stream_position=stream_position
        )
        return subscription


def callback_user_created(session, user, stream_position):
    print(user)
    db = session.client[settings.MONGO_DATABASE]
    # Setting mongo as default database temporarily and then migration creates a set of
    # collections, including api_myuser.
    users = db["api_myuser"]
    positions = db["stream_positions"]
    # Must pass the session to the operations.
    users.insert_one(user, session=session)
    positions.update_one(
        {"stream_type": "user"},
        {"$set": {"stream_position": stream_position}},
        upsert=True,
        session=session,
    )


def catch_up_user_events():
    client_esdb = ESClient("user")
    client_mongo = MongoClient(
        host=settings.MONGO_HOST,
        port=int(settings.MONGO_PORT),
        username=settings.MONGO_USERNAME,
        password=settings.MONGO_PASSWORD,
        replicaSet=settings.MONGO_RSNAME,
    )

    db = client_mongo[settings.MONGO_DATABASE]
    result = db["stream_positions"].find_one({"stream_type": "user"})
    if result:
        processed_position = result["stream_position"]
    else:
        processed_position = 0

    for event in client_esdb.subscribe(processed_position):
        stream_position = event.stream_position
        match event.type:
            case "UserCreated":
                user = json.loads(event.data)
                user["id"] = UUID(user["id"])
                # Use transaction to ensure atomicity of event processing and "acknowledgement".
                # Start a transaction, execute the callback, and commit (or abort on error).
                with client_mongo.start_session() as session:
                    session.with_transaction(
                        lambda s: callback_user_created(s, user, stream_position),
                    )
            case _:
                pass


def callback_token_blacklisted(session, token, stream_position):
    print(token)
    db = session.client[settings.MONGO_DATABASE]
    # Setting mongo as default database temporarily and then migration creates a set of
    # collections, including token_blacklist_blacklistedtoken.
    tokens = db["token_blacklist_blacklistedtoken"]
    positions = db["stream_positions"]
    # Must pass the session to the operations.
    tokens.insert_one(token, session=session)
    positions.update_one(
        {"stream_type": "token"},
        {"$set": {"stream_position": stream_position}},
        upsert=True,
        session=session,
    )


def catch_up_token_events():
    client_esdb = ESClient("token")
    client_mongo = MongoClient(
        host=settings.MONGO_HOST,
        port=int(settings.MONGO_PORT),
        username=settings.MONGO_USERNAME,
        password=settings.MONGO_PASSWORD,
        replicaSet=settings.MONGO_RSNAME,
    )

    db = client_mongo[settings.MONGO_DATABASE]
    result = db["stream_positions"].find_one({"stream_type": "token"})
    if result:
        processed_position = result["stream_position"]
    else:
        processed_position = 0

    for event in client_esdb.subscribe(processed_position):
        stream_position = event.stream_position
        match event.type:
            case "TokenBlacklisted":
                token = json.loads(event.data)
                token["blacklisted_at"] = datetime.fromisoformat(
                    token["blacklisted_at"]
                )
                # Use transaction to ensure atomicity of event processing and "acknowledgement".
                # Start a transaction, execute the callback, and commit (or abort on error).
                with client_mongo.start_session() as session:
                    session.with_transaction(
                        lambda s: callback_token_blacklisted(s, token, stream_position),
                    )
            case _:
                pass


def subscribe_events():
    # Daemon=True to terminate the threads when the main process terminates.
    # No joinning the threads so that the caller function subscribe_events
    # can finish and thus function ready can finish to let the server do the
    # work.
    thread_user = Thread(target=catch_up_user_events, daemon=True)
    thread_user.start()
    thread_token = Thread(target=catch_up_token_events, daemon=True)
    thread_token.start()


def test():
    client = ESDBClient(uri=EVENTSTOREDB_URI)
    stream_name = f"test-{str(uuid4())}"
    print(stream_name)

    expected_position = client.get_stream_position(stream_name=stream_name)
    print(expected_position)
    event1 = NewEvent(type="OrderCreated", data=b"data1")
    commit_position1 = client.append_events(
        stream_name=stream_name,
        expected_position=expected_position,
        events=[event1],
    )
    print(commit_position1)
    event2 = NewEvent(type="OrderUpdated", data=b"data2")
    event3 = NewEvent(type="OrderDeleted", data=b"data3")

    expected_position = client.get_stream_position(stream_name=stream_name)
    print(expected_position)
    commit_position2 = client.append_events(
        stream_name=stream_name,
        expected_position=expected_position,
        events=[event2, event3],
    )
    print(commit_position2)

    # Read all events recorded in a stream.
    recorded = list(client.read_stream_events(stream_name=stream_name))

    assert len(recorded) == 3
    assert recorded[0].data == event1.data
    assert recorded[1].data == event2.data
    assert recorded[2].data == event3.data
    assert recorded[0].type == event1.type
    assert recorded[1].type == event2.type
    assert recorded[2].type == event3.type

    for record in client.read_stream_events(
        stream_name="test-9166d5f2-0027-48c4-b99e-824cb4f9e537", stream_position=0
    ):
        print(record)

    client.close()


def test2():
    data = pickle.dumps({"uuid": "uuid", "password": "password1", "username": "user1"})
    client = ESClient(
        "user",
        "UserCreated",
        data,
    )

    commit_position = client.send()
    print(commit_position)

    for record in client.receive(2):
        print(record.type)
        print(pickle.loads(record.data))

    client.close()


if __name__ == "__main__":
    # test()
    test2()
