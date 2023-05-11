from uuid import uuid4
import esdbclient

# TODO: fix esdbclient.exceptions.DiscoveryFailed and use secure cluster instead of insecure single server.
#       Failed to read from gossip seed: ['esdb.node1:2111', 'esdb.node2:2112', 'esdb.node3:2113']
# ESDB_SERVERS = [
#     "esdb.node1:2111",
#     "esdb.node2:2112",
#     "esdb.node3:2113",
# ]
# EVENTSTOREDB_URI = f"esdb://{','.join(ESDB_SERVERS)}?TlsVerifyCert=false"
EVENTSTOREDB_URI = "esdb://esdb:2113?Tls=false"


def test():
    client = esdbclient.ESDBClient(uri=EVENTSTOREDB_URI)
    stream_name = f"test-{str(uuid4())}"
    print(stream_name)

    expected_position = client.get_stream_position(stream_name=stream_name)
    print(expected_position)
    event1 = esdbclient.NewEvent(type="OrderCreated", data=b"data1")
    commit_position1 = client.append_events(
        stream_name=stream_name,
        expected_position=expected_position,
        events=[event1],
    )
    print(commit_position1)
    event2 = esdbclient.NewEvent(type="OrderUpdated", data=b"data2")
    event3 = esdbclient.NewEvent(type="OrderDeleted", data=b"data3")

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


if __name__ == "__main__":
    test()
