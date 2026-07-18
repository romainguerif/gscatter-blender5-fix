def from_join_geometry(data: dict, inp, index: int):
    for link in inp.links:
        data["inputs"].append(
            [
                index,
                link.from_node.name,
                int(link.from_socket.path_from_id().split("[")[-1][:-1]),
            ]
        )
