from host.Entry import Entry, EntryType

HEAD : Entry = Entry(EntryType.PLACEHOLDER, 0x00.to_bytes())

def generate_path(topic: str):
    """Util to split the path to edge"""
    return topic.strip().split("/")

def add_entry(topic: str, type: EntryType, value: bytes):
    """Add an entry to the NT"""
    path = generate_path(topic)
    curr = HEAD

    for edge in path[:-1]:
        node = curr.get_child(edge)
        if node is None:
            node = Entry(EntryType.PLACEHOLDER, 0x00)
            curr.add_child(edge, node)
        curr = node

    node = curr.get_child(path[-1])
    if node is None:
        node = Entry(type, value)
        curr.add_child(path[-1], node)
    else:
        node.value_bytes = value
