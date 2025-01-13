def start_dos(sid, socketio, logger):
    logger.info(f'Starting DoS on sid: {sid}')
    socketio.emit('start-dos', to=sid)