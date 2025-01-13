def show_fake_banner(sid, socketio, logger):
    message = input("Message to show in banner: ").strip()
    logger.info(f'Showing fake banner on sid: {sid} with message {message}')
    socketio.emit('fake-banner', {'message': message}, to=sid)

def destroy_fake_banner(sid, socketio, logger):
    logger.info(f'Destroying fake banner on sid: {sid}')
    socketio.emit('destroy-fake-banner', to=sid)