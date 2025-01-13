def request_config(socketio, sid, logger):
    socketio.emit('get-config', to=sid)
    logger.info(f'Requested config from client with sid: {sid}.')

def request_appObject(socketio, sid, logger):
    socketio.emit('get-appObject', to=sid)
    logger.info(f'Requested appObject from client with sid: {sid}.')

def request_appMgr(socketio, sid, logger):
    socketio.emit('get-appMgr', to=sid)
    logger.info(f'Requested appMgr from client with sid: {sid}.')
