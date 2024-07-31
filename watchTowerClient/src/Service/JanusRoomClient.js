import Janus from './janus';

class VideoRoomClient {
    constructor(serverUrl, roomId, onStreamAdded, onStreamRemoved) {
        this.serverUrl = serverUrl;
        this.roomId = roomId;
        this.onStreamAdded = onStreamAdded;
        this.onStreamRemoved = onStreamRemoved;
        this.janus = null;
        this.roomHandle = null;
        this.myid = null;
        this.mypvtid = null;
        this.subscribers = {};
        this.opaqueId = "videoroom-" + Janus.randomString(12);
    }

    init() {
        return new Promise((resolve, reject) => {
            Janus.init({
                debug: "warning",
                callback: () => {
                    if (!Janus.isWebrtcSupported()) {
                        reject(new Error('No WebRTC support'));
                        return;
                    }
                    this.connectToJanus().then(resolve).catch(reject);
                }
            });
        });
    }

    connectToJanus() {
        return new Promise((resolve, reject) => {
            this.janus = new Janus({
                server: this.serverUrl,
                success: () => {
                    this.attachPlugin().then(resolve).catch(reject);
                },
                error: (error) => reject(new Error('Janus error: ' + error)),
                // destroyed: () => console.log('Janus destroyed')
            });
        });
    }

    attachPlugin() {
        return new Promise((resolve, reject) => {
            this.janus.attach({
                plugin: "janus.plugin.videoroom",
                opaqueId: this.opaqueId,
                success: (pluginHandle) => {
                    this.roomHandle = pluginHandle;
                    this.joinRoom().then(resolve).catch(reject);
                },
                error: (error) => reject(new Error('Error attaching to VideoRoom plugin: ' + error)),
                onmessage: (msg, jsep) => this.handleMessage(msg, jsep),
                // onlocaltrack: (track, on) => console.log('Local track', on ? 'added' : 'removed', track),
                // onremotetrack: (track, mid, on) => console.log('Remote track', on ? 'added' : 'removed', track, 'mid:', mid),
                // oncleanup: () => console.log('VideoRoom plugin cleaned up')
            });
        });
    }

    joinRoom() {
        return new Promise((resolve, reject) => {
            const join = {
                request: "join",
                room: this.roomId,
                ptype: "publisher",
                display: "User " + Janus.randomString(5)
            };
            this.roomHandle.send({
                message: join,
                success: () => resolve(),
                error: (error) => reject(new Error('Error joining room: ' + error))
            });
        });
    }

    handleMessage(msg, jsep) {
        const event = msg["videoroom"];
        if (event) {
            switch (event) {
                case "joined":
                    this.myid = msg["id"];
                    this.mypvtid = msg["private_id"];
                    // console.log("Successfully joined room", msg["room"]);
                    if (msg["publishers"]) {
                        this.handleNewPublishers(msg["publishers"]);
                    }
                    break;
                case "event":
                    if (msg["publishers"]) {
                        this.handleNewPublishers(msg["publishers"]);
                    } else if (msg["leaving"]) {
                        this.handleLeavingPublisher(msg["leaving"]);
                    } else if (msg["unpublished"]) {
                        this.handleUnpublish(msg["unpublished"]);
                    }
                    break;
            }
        }
        if (jsep) {
            this.roomHandle.handleRemoteJsep({ jsep: jsep });
        }
    }

    handleNewPublishers(publishers) {
        publishers.forEach(publisher => {
            if (!publisher.dummy) {
                console.log("publisher --> ", publisher)
                this.subscribeToFeed(publisher.id, publisher.streams);
            }
        });
    }

    handleLeavingPublisher(leaving) {
        this.onStreamRemoved(leaving);
        if (this.subscribers[leaving]) {
            this.subscribers[leaving].detach();
            delete this.subscribers[leaving];
        }
    }

    handleUnpublish(unpublished) {
        this.handleLeavingPublisher(unpublished);
    }

    subscribeToFeed(publisherId, streams) {
        if (this.subscribers[publisherId]) {
            return;
        }
        this.janus.attach({
            plugin: "janus.plugin.videoroom",
            opaqueId: this.opaqueId,
            success: (pluginHandle) => {
                this.subscribers[publisherId] = pluginHandle;
                const subscribe = {
                    request: "join",
                    room: this.roomId,
                    ptype: "subscriber",
                    feed: publisherId,
                    streams: streams.map(s => ({ feed: publisherId, mid: s.mid }))
                };
                pluginHandle.send({ message: subscribe });
            },
            error: (error) => console.error('Error attaching plugin for feed:', publisherId, error),
            onmessage: (msg, jsep) => this.handleSubscriberMessage(publisherId, msg, jsep),
            onremotetrack: (track, mid, on) => this.handleSubscriberTrack(publisherId, track, mid, on),
            // oncleanup: () => console.log(`Feed ${publisherId} cleaned up`)
        });
    }

    handleSubscriberMessage(publisherId, msg, jsep) {
        if (jsep) {
            this.subscribers[publisherId].createAnswer({
                jsep: jsep,
                tracks: [{ type: 'data' }],
                success: (jsep) => {
                    const body = { request: "start", room: this.roomId };
                    this.subscribers[publisherId].send({ message: body, jsep: jsep });
                },
                error: (error) => console.error('Error creating answer:', error)
            });
        }
    }

    handleSubscriberTrack(publisherId, track, mid, on) {
        if (on) {
            const stream = new MediaStream([track]);
            console.log(publisherId, track, mid, on)
            this.onStreamAdded(publisherId, mid, stream);
        } else {
            this.onStreamRemoved(publisherId, mid);
        }
    }

    destroy() {
        if (this.janus) {
            this.janus.destroy();
        }
    }
}

export default VideoRoomClient;