const ROOM_ID = 1122;
const SERVER_URL = 'http://localhost:8088/janus';

class JanusVideoRoom {
    constructor() {
        this.janus = null;
        this.roomHandle = null;
        this.myid = null;
        this.mypvtid = null;
        this.mystream = null;
        this.subscribers = {};
        this.feedStreams = {};
        this.opaqueId = "videoroom-" + Janus.randomString(12);
        this.pendingPlaybacks = new Set();
    }

    init() {
        return new Promise((resolve, reject) => {
            Janus.init({
                debug: "all",
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
                server: SERVER_URL,
                success: () => {
                    this.attachPlugin().then(resolve).catch(reject);
                },
                error: (error) => reject(new Error('Janus error: ' + error)),
                destroyed: () => console.log('Janus destroyed')
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
                consentDialog: (on) => console.log('Consent dialog:', on),
                iceState: (state) => console.log(`ICE state is ${state}`),
                mediaState: (medium, on, mid) => {
                    console.log("Janus " + (on ? "started" : "stopped") + " receiving our " + medium + " (mid=" + mid + ")");
                },
                webrtcState: (on) => {
                    console.log("Janus says our WebRTC PeerConnection is " + (on ? "up" : "down") + " now");
                },
                slowLink: (uplink, lost, mid) => {
                    console.warn("Janus reports problems " + (uplink ? "sending" : "receiving") +
                        " packets on mid " + mid + " (" + lost + " lost packets)");
                },
                onmessage: (msg, jsep) => this.handleMessage(msg, jsep),
                onlocaltrack: (track, on) => this.handleLocalTrack(track, on),
                onremotetrack: (track, mid, on) => this.handleRemoteTrack(track, mid, on),
                oncleanup: () => {
                    console.log('VideoRoom plugin cleaned up');
                    delete this.feedStreams[this.myid];
                }
            });
        });
    }

    joinRoom() {
        return new Promise((resolve, reject) => {
            const join = {
                request: "join",
                room: ROOM_ID,
                ptype: "publisher",
                display: "User " + Janus.randomString(5)
            };
            this.roomHandle.send({
                message: join,
                success: () => {
                    console.log("Successfully joined room", ROOM_ID);
                    resolve();
                },
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
                    console.log("Successfully joined room", msg["room"]);
                    console.log("My IDs:", this.myid, this.mypvtid);
                    if (msg["publishers"]) {
                        this.handleNewPublishers(msg["publishers"]);
                    }
                    this.roomHandle.send({ message: { request: "listparticipants", room: ROOM_ID } });
                    break;
                case "event":
                    if (msg["streams"]) {
                        this.handleStreams(msg["streams"]);
                    } else if (msg["publishers"]) {
                        this.handleNewPublishers(msg["publishers"]);
                    } else if (msg["leaving"]) {
                        this.handleLeavingPublisher(msg["leaving"]);
                    } else if (msg["unpublished"]) {
                        this.handleUnpublish(msg["unpublished"]);
                    } else if (msg["error"]) {
                        console.error("Error:", msg["error"]);
                    }
                    break;

                case "participants":
                    if (msg["participants"]) {
                        this.handleExistingParticipants(msg["participants"]);
                    }
                    break;
                case "destroyed":
                    console.warn("Room destroyed!");
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
                console.log("New publisher:", publisher);
                this.feedStreams[publisher.id] = publisher.streams;
                this.subscribeToFeed(publisher.id, publisher.streams);
            }
        });
    }

    handleExistingParticipants(participants) {
        console.log("Handling existing participants:", participants);
        participants.forEach(participant => {
            if (participant.publisher && !this.feedStreams[participant.id]) {
                console.log("Existing publisher found:", participant);
                this.feedStreams[participant.id] = participant.streams;
                this.subscribeToFeed(participant.id, participant.streams);
            }
        });
    }

    handleLeavingPublisher(leaving) {
        console.log("Publisher leaving:", leaving);
        delete this.feedStreams[leaving];
        this.removeVideoElement(leaving);
    }

    handleUnpublish(unpublished) {
        console.log("Publisher unpublished:", unpublished);
        this.removeVideoElement(unpublished);
        this.pendingPlaybacks.delete(unpublished);
        this.updatePlayAllButton();
        delete this.feedStreams[unpublished];
        if (this.subscribers[unpublished]) {
            this.subscribers[unpublished].detach({
                success: () => console.log(`Successfully detached from feed ${unpublished}`),
                error: (error) => console.error(`Error detaching from feed ${unpublished}:`, error)
            });
            delete this.subscribers[unpublished];
        }
    }

    removeVideoElement(publisherId) {
        const videoRemote = document.getElementById(`videoremote-${publisherId}`);
        if (videoRemote) {
            videoRemote.remove();
        }
    }

    subscribeToFeed(publisherId, streams) {
        if (this.subscribers[publisherId]) {
            console.log(`Already subscribed to feed ${publisherId}`);
            return;
        }
        console.log(`Subscribing to feed ${publisherId}`, streams);


        this.janus.attach({
            plugin: "janus.plugin.videoroom",
            opaqueId: this.opaqueId,
            success: (pluginHandle) => {
                console.log(`Successfully attached to plugin for feed ${publisherId}`);
                this.subscribers[publisherId] = pluginHandle;
                const subscribe = {
                    request: "join",
                    room: ROOM_ID,
                    ptype: "subscriber",
                    feed: publisherId,
                    streams: streams.map(s => ({ feed: publisherId, mid: s.mid }))
                };
                pluginHandle.send({ 
                    message: subscribe,
                    success: () => console.log(`Join request sent for feed ${publisherId}`),
                    error: (error) => console.error(`Error sending join request for feed ${publisherId}:`, error)
                });
            },
            error: (error) => console.error('Error attaching plugin for feed:', publisherId, error),
            onmessage: (msg, jsep) => this.handleSubscriberMessage(publisherId, msg, jsep),
            onremotetrack: (track, mid, on) => this.handleSubscriberTrack(publisherId, track, mid, on),
            oncleanup: () => console.log(`Feed ${publisherId} cleaned up`)
        });
    }

    handleSubscriberMessage(publisherId, msg, jsep) {
        const event = msg["videoroom"];
        console.log(`Subscriber message for feed ${publisherId}:`, msg);

        if (msg["error"]) {
            console.error("Subscriber error:", msg["error"]);
            return;
        }

        if (event === "attached") {
            console.log(`Successfully subscribed to feed ${publisherId}`);
        }

        if (jsep) {
            console.log(`Handling remote SDP for feed ${publisherId}:`, jsep);
            this.subscribers[publisherId].createAnswer({
                jsep: jsep,
                tracks: [{ type: 'data' }],
                success: (jsep) => {
                    console.log(`Answer created for feed ${publisherId}:`, jsep);
                    const body = { request: "start", room: ROOM_ID };
                    this.subscribers[publisherId].send({ 
                        message: body, 
                        jsep: jsep,
                        success: () => console.log(`Start request sent for feed ${publisherId}`),
                        error: (error) => console.error(`Error sending start request for feed ${publisherId}:`, error)
                    });
                },
                error: (error) => console.error('Error creating answer:', error)
            });
        }
    }

    handleLocalTrack(track, on) {
        console.log('Local track', on ? 'added' : 'removed', track);
    }

    handleRemoteTrack(track, mid, on) {
        console.log('Remote track', on ? 'added' : 'removed', track);
    }

    handleSubscriberTrack(publisherId, track, mid, on) {
        console.log(`Subscriber track from feed ${publisherId}`, on ? 'added' : 'removed', track, 'mid:', mid);
        
        if (!on) {
            this.removeVideoTrack(publisherId, mid);
            return;
        }

        const stream = new MediaStream([track]);
        this.createOrUpdateVideoElement(publisherId, mid, stream);

        // Log track settings
        console.log(`Track settings for feed ${publisherId}:`, track.getSettings());
    }

    removeVideoTrack(publisherId, mid) {
        const videoElement = document.getElementById(`video-${publisherId}-${mid}`);
        if (videoElement) {
            videoElement.remove();
        }
        this.checkAndAddPlaceholder(publisherId);
    }

    createOrUpdateVideoElement(publisherId, mid, stream) {
        console.log(`Creating/updating video element for feed ${publisherId}, mid ${mid}`);
        let videoContainer = document.getElementById(`videoremote-${publisherId}`);
        if (!videoContainer) {
            videoContainer = document.createElement('div');
            videoContainer.id = `videoremote-${publisherId}`;
            document.body.appendChild(videoContainer);
        }

        let videoElement = document.getElementById(`video-${publisherId}-${mid}`);
        if (!videoElement) {
            videoElement = document.createElement('video');
            videoElement.id = `video-${publisherId}-${mid}`;
            videoElement.playsInline = true;
            videoContainer.appendChild(videoElement);
        }

        this.removePlaceholder(publisherId);
        
        try {
            Janus.attachMediaStream(videoElement, stream);
            console.log(`MediaStream attached to video element for feed ${publisherId}`);
        } catch (error) {
            console.error(`Error attaching MediaStream for feed ${publisherId}:`, error);
        }
        
        // Add event listeners
        videoElement.onerror = (e) => console.error(`Error with video element for feed ${publisherId}:`, e);
        videoElement.onloadedmetadata = () => console.log(`Video metadata loaded for feed ${publisherId}`);
        videoElement.onplaying = () => console.log(`Video for feed ${publisherId} started playing`);

        // Add to pending playbacks
        this.pendingPlaybacks.add(publisherId);
        this.updatePlayAllButton();

        // Log video element properties
        console.log(`Video element properties for feed ${publisherId}:`, {
            readyState: videoElement.readyState,
            paused: videoElement.paused,
            currentTime: videoElement.currentTime,
            videoWidth: videoElement.videoWidth,
            videoHeight: videoElement.videoHeight
        });
    }

    updatePlayAllButton() {
        let playAllButton = document.getElementById('play-all-button');
        if (this.pendingPlaybacks.size > 0) {
            if (!playAllButton) {
                playAllButton = document.createElement('button');
                playAllButton.id = 'play-all-button';
                playAllButton.textContent = 'Play All Videos';
                playAllButton.onclick = () => this.playAllVideos();
                document.body.insertBefore(playAllButton, document.body.firstChild);
            }
            playAllButton.textContent = `Play All Videos (${this.pendingPlaybacks.size})`;
        } else if (playAllButton) {
            playAllButton.remove();
        }
    }

    playAllVideos() {
        this.pendingPlaybacks.forEach(publisherId => {
            const videoElement = document.querySelector(`#videoremote-${publisherId} video`);
            if (videoElement) {
                videoElement.play().then(() => {
                    console.log(`Playback started for feed ${publisherId}`);
                    this.pendingPlaybacks.delete(publisherId);
                    this.updatePlayAllButton();
                }).catch(error => {
                    console.error(`Error starting playback for feed ${publisherId}:`, error);
                });
            }
        });
    }
    
    showPlayButton(videoElement, publisherId) {
        const playButton = document.createElement('button');
        playButton.textContent = 'Play Video';
        playButton.onclick = () => {
            videoElement.play().then(() => {
                console.log(`Playback started for feed ${publisherId} after user interaction`);
                playButton.remove();
            }).catch(error => {
                console.error(`Error starting playback for feed ${publisherId} after user interaction:`, error);
            });
        };
        videoElement.parentNode.insertBefore(playButton, videoElement.nextSibling);
    }

    checkAndAddPlaceholder(publisherId) {
        const remainingVideoTracks = document.querySelectorAll(`[id^=video-${publisherId}-]`).length;
        if (remainingVideoTracks === 0) {
            const placeholderHtml = `
                <div id="no-video-${publisherId}" class="no-video-container">
                    <i class="fa-solid fa-video fa-xl no-video-icon"></i>
                    <span class="no-video-text">No remote video available</span>
                </div>`;
            const videoContainer = document.getElementById(`videoremote-${publisherId}`);
            if (videoContainer) {
                videoContainer.innerHTML = placeholderHtml;
            }
        }
    }

    removePlaceholder(publisherId) {
        const placeholder = document.getElementById(`no-video-${publisherId}`);
        if (placeholder) {
            placeholder.remove();
        }
    }

    publishOwnFeed(useAudio = false) {
        this.roomHandle.createOffer({
            tracks: [
                { type: 'video', capture: true, recv: false }
            ],
            success: (jsep) => {
                const publish = { request: "configure", audio: useAudio, video: true };
                this.roomHandle.send({ message: publish, jsep: jsep });
            },
            error: (error) => console.error('Error publishing:', error)
        });
    }

    
}

// Usage
document.addEventListener('DOMContentLoaded', () => {
    const videoRoom = new JanusVideoRoom();
    videoRoom.init().then(() => {
        console.log('Janus VideoRoom initialized successfully 2026');
        // Optionally publish your own feed
        // videoRoom.publishOwnFeed();
    }).catch(error => {
        console.error('Failed to initialize Janus VideoRoom:', error);
    });
});



