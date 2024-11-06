class URLBuilder:

    def __init__(self,
                 protocol: str,
                 host: str,
                 port: str | int | None = None,
                 path: list[str] = []):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.path = path

    def _path(self) -> str:
        match len(self.path):
            case 0:
                return ''
            case _:
                if self.path[-1][-1] != '/':
                    return '/'.join(self.path) + '/'
                else:
                    return '/'.join(self.path)

    def _semicoloned_port(self) -> str | None:
        if self.port:
            return ':' + str(self.port)
        else:
            return str(self.port)

    def url(self):
        url_list = [self.protocol,
                    '://', self.host,
                    self._semicoloned_port(),
                    '/', self._path()]
        url = ''.join(url_list)
        return url
