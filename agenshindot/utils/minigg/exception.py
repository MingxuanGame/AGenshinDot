class NotFoundError(Exception):
    def __init__(self, type_: str, name: str):
        self.name = name
        self.type_ = type_

    def __str__(self) -> str:
        return f"no such {self.type_}: {self.name}"

    def __repr__(self) -> str:
        return f"<NotFoundError type={self.type_} name={self.name}>"


class APINotFound(Exception):
    def __init__(self, api: str):
        self.api = api

    def __str__(self) -> str:
        return f"no such {self.api}"

    def __repr__(self) -> str:
        return f"<APINotFound api={self.api}>"
