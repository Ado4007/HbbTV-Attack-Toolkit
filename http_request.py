import json

import prompt

def http_request_from_client_selection(client, socketio, logger):
    print('Select to which local IP to send the request:')
    if client.scan is None:
        print('Nothing to select! Run network scan on this client first!')
        return
    options = list(client.scan.get("network").keys())
    sel = prompt.menu(options)
    port = input('Port (default 80): ')
    if port != '':
        port = f':{port}'
    url = input(f'URL: http://{sel}{port}/')
    url = f'http://{sel}{port}/{url}'
    http_request_send(client, url, socketio, logger)


def http_request_from_url(client, socketio, logger):
    url = input('URL to request: ')
    http_request_send(client, url, socketio, logger)

def http_request_send(client, url, socketio, logger):
    method = request_method()
    body = input('Request body (empty for none): ')
    try: 
        if body == '':
            body = None
        else:
            body = json.loads(body)
        headers = input('Request headers (empty for none): ')
        if headers == '':
            headers = None
        else:
            headers = json.loads(headers)
    except json.JSONDecodeError:
        logger.error('Error happened when parsing body and headers! Returning...')
        return
    
    logger.info(f'Requesting {method} {url} from sid: {client.sid}.')
    socketio.emit('send-request', {
        'url': url,
        'method': method,
        'body': body,
        'headers': headers
    }, to=client.sid)


def request_method():
    print('Select the request method:')
    options = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD",
        "OPTIONS",
    ]
    return prompt.menu(options)