from utils.UrlBuilder import UrlBuilder


def before(name):
    print '----------'
    print 'current test: ' + name
    print 'test started!'


def after(result):
    print 'test result: ' + str(result)
    print '----------'


def test_url_builder():
    before('test url builder')

    builder = UrlBuilder()
    url1 = builder.schema(UrlBuilder.SCHEMA_HTTPS).host('www.huhaoyu.com').segment('path1') \
        .segments(['path2', 'path3']).build()

    builder = UrlBuilder()
    url2 = builder.host('www.huhaoyu.com').build()
    success = url1 == 'https://www.huhaoyu.com/path1/path2/path3' and url2 == 'http://www.huhaoyu.com/'

    after(success)


# -----------------------
# run tests
# -----------------------

test_url_builder()
