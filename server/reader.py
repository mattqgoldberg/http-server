def read_file(path: str) -> bytes | None:
    try:
        with open(path, 'rb') as f:
            bytes_data = f.read()


        return bytes_data
    except Exception as e:
        print(e)
        return None

