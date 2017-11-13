import requests


def post_request(url, data=None):
    """Mock POST request"""

    if 'slack.com/api/rtm.connect' in url:
        return mock_rtm_connect(data)
    else:
        return mock_no_response()


def mock_rtm_connect(data):
    """Mock request to Slack RTM API (https://slack.com/api/rtm.connect)"""

    response = requests.Response()

    if data.get('token') == 'good-token':
        response.status_code = 200
        response._content = b'{"url": "websock.et/url",' \
                            b'"ok": true}'
    elif data.get('token') == 'bad-token':
        response.status_code = 200
        response._content = b'{"ok": false}'
    else:
        response.status_code = 401
        response._content = b'{}'

    return response


def mock_no_response():
    """Mock 404 request"""

    response = requests.Response()
    response.status_code = 404
    response._content = b'{}'

    return response
