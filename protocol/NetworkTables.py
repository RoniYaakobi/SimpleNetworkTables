from protocol.Entry import Entry, EntryType, generate_path

HEAD : Entry = Entry.create_null()

def add_entry(topic: str, type: EntryType, value: bytes):
    """Add an entry to the NT"""
    path = generate_path(topic)
    curr = HEAD

    for idx,edge in enumerate(path[:-1]):
        node = curr.get_child(edge)
        if node is None:
            node = Entry.create_null("/".join(path[:idx + 1]))
            curr.add_child(edge, node)
        curr = node

    node = curr.get_child(path[-1])
    if node is None:
        node = Entry(topic, type, value)
        curr.add_child(path[-1], node)
    else:
        node.value_bytes = value
