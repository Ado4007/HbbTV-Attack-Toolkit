def channel_switch_next(sid, socketio, logger):
    logger.info(f'Switching to next channel on sid: {sid}')
    socketio.emit('next-channel', to=sid)

def channel_switch_prev(sid, socketio, logger):
    logger.info(f'Switching to previous channel on sid: {sid}')
    socketio.emit('prev-channel', to=sid)