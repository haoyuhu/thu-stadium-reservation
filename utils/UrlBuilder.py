class UrlBuilder:
    SCHEMA_HTTP = 'http'
    SCHEMA_HTTPS = 'https'

    def __init__(self, schema=SCHEMA_HTTP):
        """
        create url builder
        :param schema: http or https
        """
        self._segments = []
        self._host = ''
        self._schema = schema

    def schema(self, schema):
        """
        add schema of this url
        :param schema: http or https
        :return: this builder
        """
        self._schema = schema
        return self

    def host(self, host):
        """
        add host of this url
        :param host: string of host
        :return: this builder
        """
        self._host = host
        return self

    def segment(self, segment):
        """
        add path segment of this url
        :param segment: string of path segment
        :return: this builder
        """
        self._segments.append(segment)
        return self

    def segments(self, segments):
        """
        add path segments of this url
        :param segments: array of path segment
        :return: this builder
        """
        self._segments.extend(segments)
        return self

    def build(self):
        """
        create a string of url
        :return: url
        """
        if self._schema is not None and self._host is not None:
            ret = self._schema
            ret += '://' + self._host
            if self._segments:
                for segment in self._segments:
                    ret += '/' + segment
            else:
                ret += '/'
            return ret
        return False
