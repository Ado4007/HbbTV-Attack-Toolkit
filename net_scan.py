import prompt

def start_netscan(sid, socketio, logger):
    sel = prompt.menu_index([
        "RTC Localhost detect On",
        "RTC Localhost detect Off"
    ])
    isRtc = sel == 0
    ips_str = input("Input the subnets to scan (split by comma, leave empty for default): ")
    if (ips_str == ''):
        ips = None
    else:
        ips = [ip.strip() for ip in ips_str.split(',')]
    logger.info(f'Starting netscan on sid: {sid}. isRtc = {isRtc}. ips = {ips}')
    logger.warn(f'Network scanning usually takes longer. Please be patient, if scan succesful, results will show in netscan/ folder')
    logger.warn(f'If no results after more than 30 minutes, the network scan might have failed!')
    socketio.emit('start-netscan', {"isRtc": isRtc, "ips": ips}, to=sid)