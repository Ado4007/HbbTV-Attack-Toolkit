const root =
    (typeof globalThis !== "undefined" && globalThis) ||
    (typeof self !== "undefined" && self) ||
    (typeof global !== "undefined" && global);

const EventTarget = (function() {
    function EventTarget() {
        this.__listeners = new Map();
    }

    EventTarget.prototype = Object.create(Object.prototype);

    EventTarget.prototype.addEventListener = function(
        type,
        listener,
        options
    ) {
        if (arguments.length < 2) {
            throw new TypeError(
                "TypeError: Failed to execute 'addEventListener' on 'EventTarget': 2 arguments required, but only " + arguments.length + " present."
            );
        }
        const __listeners = this.__listeners;
        const actualType = type.toString();
        if (!__listeners.has(actualType)) {
            __listeners.set(actualType, new Map());
        }
        const listenersForType = __listeners.get(actualType);
        if (!listenersForType.has(listener)) {
            // Any given listener is only registered once
            listenersForType.set(listener, options);
        }
    };

    EventTarget.prototype.removeEventListener = function(
        type,
        listener,
        _options
    ) {
        if (arguments.length < 2) {
            throw new TypeError(
                "TypeError: Failed to execute 'addEventListener' on 'EventTarget': 2 arguments required, but only " + arguments.length + " present."
            );
        }
        const __listeners = this.__listeners;
        const actualType = type.toString();
        if (__listeners.has(actualType)) {
            const listenersForType = __listeners.get(actualType);
            if (listenersForType.has(listener)) {
                listenersForType.delete(listener);
            }
        }
    };

    EventTarget.prototype.dispatchEvent = function(event) {
        if (!(event instanceof Event)) {
            throw new TypeError(
                "Failed to execute 'dispatchEvent' on 'EventTarget': parameter 1 is not of type 'Event'."
            );
        }
        const type = event.type;
        const __listeners = this.__listeners;
        const listenersForType = __listeners.get(type);
        if (listenersForType) {
            for (var listnerEntry of listenersForType.entries()) {
                const listener = listnerEntry[0];
                const options = listnerEntry[1];

                try {
                    if (typeof listener === "function") {
                        // Listener functions must be executed with the EventTarget as the `this` context.
                        listener.call(this, event);
                    } else if (listener && typeof listener.handleEvent === "function") {
                        // Listener objects have their handleEvent method called, if they have one
                        listener.handleEvent(event);
                    }
                } catch (err) {
                    // We need to report the error to the global error handling event,
                    // but we do not want to break the loop that is executing the events.
                    // Unfortunately, this is the best we can do, which isn't great, because the
                    // native EventTarget will actually do this synchronously before moving to the next
                    // event in the loop.
                    setTimeout(() => {
                        throw err;
                    });
                }
                if (options && options.once) {
                    // If this was registered with { once: true }, we need
                    // to remove it now.
                    listenersForType.delete(listener);
                }
            }
        }
        // Since there are no cancellable events on a base EventTarget,
        // this should always return true.
        return true;
    };

    return EventTarget;
})();

if (typeof root.AbortController === "undefined") {
    const SECRET = {};

    root.AbortSignal = (function() {
        function AbortSignal(secret) {
            if (secret !== SECRET) {
                throw new TypeError("Illegal constructor...");
            }
            EventTarget.call(this);
            this._aborted = false;
        }

        AbortSignal.prototype = Object.create(EventTarget.prototype);
        AbortSignal.prototype.constructor = AbortSignal;

        Object.defineProperty(AbortSignal.prototype, "onabort", {
            get: function() {
                return this._onabort;
            },
            set: function(callback) {
                const existing = this._onabort;
                if (existing) {
                    this.removeEventListener("abort", existing);
                }
                this._onabort = callback;
                this.addEventListener("abort", callback);
            },
        });

        Object.defineProperty(AbortSignal.prototype, "aborted", {
            get: function() {
                return this._aborted;
            },
        });

        return AbortSignal;
    })();

    root.AbortController = (function() {
        function AbortController() {
            this._signal = new AbortSignal(SECRET);
        }

        AbortController.prototype = Object.create(Object.prototype);

        Object.defineProperty(AbortController.prototype, "signal", {
            get: function() {
                return this._signal;
            },
        });

        AbortController.prototype.abort = function() {
            const signal = this.signal;
            if (!signal.aborted) {
                signal._aborted = true;
                signal.dispatchEvent(new Event("abort"));
            }
        };

        return AbortController;
    })();
}