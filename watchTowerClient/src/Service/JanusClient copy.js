import Janus from "@nabla/janus-client";

class JanusVideoRoomClient {
  constructor(serverUrl, roomId) {
    this.serverUrl = serverUrl;
    this.roomId = roomId;
    this.janus = null;
    this.roomHandle = null;
    this.opaqueId = `videoroom-${Janus.randomString(12)}`;
    this.feedStreams = {};
    this.onStreamAddedCallbacks = [];
    this.onStreamRemovedCallbacks = [];
    this.myid = null;
    this.mypvtid = null;
  }

  init() {
    return new Promise((resolve, reject) => {
      Janus.init({
        debug: "all",
        callback: () => {
          if (!Janus.isWebrtcSupported()) {
            reject(new Error("No WebRTC support"));
            return;
          }
          this.connectToJanus().then(resolve).catch(reject);
        },
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
        error: (error) => reject(new Error(`Janus error: ${error}`)),
        destroyed: () => console.log("Janus destroyed"),
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
        error: (error) =>
          reject(new Error(`Error attaching to VideoRoom plugin: ${error}`)),
        onmessage: (msg, jsep) => this.handleMessage(msg, jsep),
        oncleanup: () => {
          console.log("VideoRoom plugin cleaned up");
          this.feedStreams = {};
        },
      });
    });
  }

  joinRoom() {
    return new Promise((resolve, reject) => {
      const join = {
        request: "join",
        room: this.roomId,
        ptype: "publisher",
        display: "User " + Janus.randomString(5),
        // feed: null
      };
      this.roomHandle.send({
        message: join,
        success: () => {
          console.log("Successfully joined room as subscriber");
          resolve();
          // this.listParticipants()
          //   .then(resolve)
          //   .catch(reject);
        },
        error: (error) => reject(new Error(`Error joining room: ${error}`)),
      });
    });
  }

  listParticipants() {
    return new Promise((resolve, reject) => {
      this.roomHandle.send({
        message: { request: "listparticipants", room: this.roomId },
        success: (response) => {
          console.log("Participants list:", response);
          if (response.participants) {
            this.handleExistingParticipants(response.participants);
          }
          resolve(response.participants);
        },
        error: (error) =>
          reject(new Error(`Error requesting participants list: ${error}`)),
      });
    });
  }

  handleMessage(msg, jsep) {
    const event = msg["videoroom"];
    console.log("Received message:", msg);

    if (event) {
      switch (event) {
        case "joined":
          this.myid = msg["id"];
          this.mypvtid = msg["private_id"];
          if (msg["publishers"]) {
            this.handleNewPublishers(msg["publishers"]);
          }
          this.listParticipants();
          break;
        case "event":
          if (msg["publishers"]) {
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
    console.log("New publishers:", publishers);
    publishers.forEach((publisher) => {
      if (!publisher.dummy) {
        console.log(`Processing publisher ${publisher.id}`);
        if (this.feedStreams[publisher.id]) {
          console.log(
            `Already have streams for publisher ${publisher.id}`,
            this.feedStreams[publisher.id]
          );
        } else {
          console.log(
            `New publisher ${publisher.id}, streams:`,
            publisher.streams
          );
          this.feedStreams[publisher.id] = {};
        }
        this.subscribeToFeed(publisher.id, publisher.streams);
      }
    });
  }

  handleExistingParticipants(participants) {
    console.log("Handling existing participants:", participants);
    participants.forEach((participant) => {
      if (participant.publisher && !this.feedStreams[participant.id]) {
        console.log("Existing publisher found:", participant);
        this.subscribeToFeed(participant.id, participant.streams);
      }
    });
  }

  handleLeavingPublisher(leaving) {
    console.log("Publisher leaving:", leaving);
    delete this.feedStreams[leaving];
    this.onStreamRemovedCallbacks.forEach((callback) => callback(leaving));
  }

  handleUnpublish(unpublished) {
    console.log("Publisher unpublished:", unpublished);
    delete this.feedStreams[unpublished];
    this.onStreamRemovedCallbacks.forEach((callback) => callback(unpublished));
  }

  subscribeToFeed(publisherId, streams) {
    console.log(`Attempting to subscribe to feed ${publisherId}`, streams);
    if (Object.keys(this.feedStreams[publisherId] || {}).length > 0) {
      console.log(`Already subscribed to all streams for feed ${publisherId}`);
      return;
    }

    this.janus.attach({
      plugin: "janus.plugin.videoroom",
      opaqueId: this.opaqueId,
      success: (pluginHandle) => {
        console.log(`Successfully attached to plugin for feed ${publisherId}`);
        const subscribe = {
          request: "join",
          room: this.roomId,
          ptype: "subscriber",
          feed: publisherId,
          streams: streams.map((s) => ({ feed: publisherId, mid: s.mid })),
        };
        pluginHandle.send({
          message: subscribe,
          success: () =>
            console.log(`Join request sent for feed ${publisherId}`),
          error: (error) =>
            console.error(
              `Error sending join request for feed ${publisherId}:`,
              error
            ),
        });
      },
      error: (error) =>
        console.error("Error attaching plugin for feed:", publisherId, error),
      onmessage: (msg, jsep) =>
        this.handleSubscriberMessage(publisherId, msg, jsep, pluginHandle),
      onremotetrack: (track, mid, on) =>
        this.handleRemoteTrack(track, mid, on, publisherId),
      oncleanup: () => {
        console.log(`Feed ${publisherId} cleaned up`);
        delete this.feedStreams[publisherId];
      },
    });
  }

  handleSubscriberMessage(publisherId, msg, jsep, pluginHandle) {
    const event = msg["videoroom"];
    console.log(`Subscriber message for feed ${publisherId}:`, msg);

    if (msg["error"]) {
      console.error("Subscriber error:", msg["error"]);
      return;
    }

    if (event === "attached") {
      console.log(`Successfully subscribed to feed ${publisherId}`);
      // You might want to trigger some UI update here
    }

    if (jsep) {
      console.log(`Handling remote SDP for feed ${publisherId}:`, jsep);
      pluginHandle.createAnswer({
        jsep: jsep,
        tracks: [{ type: "data" }],
        success: (jsep) => {
          console.log(`Answer created for feed ${publisherId}:`, jsep);
          const body = { request: "start", room: this.roomId };
          pluginHandle.send({
            message: body,
            jsep: jsep,
            success: () =>
              console.log(`Start request sent for feed ${publisherId}`),
            error: (error) =>
              console.error(
                `Error sending start request for feed ${publisherId}:`,
                error
              ),
          });
        },
        error: (error) => console.error("Error creating answer:", error),
      });
    }
  }

  handleRemoteTrack(track, mid, on, publisherId) {
    console.log(
      `Remote track ${on ? "added" : "removed"}:`,
      publisherId,
      mid,
      track
    );

    if (on) {
      const stream = new MediaStream([track]);
      if (!this.feedStreams[publisherId]) {
        this.feedStreams[publisherId] = {};
      }
      this.feedStreams[publisherId][mid] = stream;
      console.log(`New stream added for publisher ${publisherId}, mid ${mid}`);
      this.onStreamAddedCallbacks.forEach((callback) =>
        callback(publisherId, mid, stream)
      );
    } else {
      if (this.feedStreams[publisherId]) {
        delete this.feedStreams[publisherId][mid];
        console.log(`Stream removed for publisher ${publisherId}, mid ${mid}`);
        if (Object.keys(this.feedStreams[publisherId]).length === 0) {
          delete this.feedStreams[publisherId];
        }
      }
      this.onStreamRemovedCallbacks.forEach((callback) =>
        callback(publisherId, mid)
      );
    }
  }

  onStreamAdded(callback) {
    this.onStreamAddedCallbacks.push(callback);
  }

  onStreamRemoved(callback) {
    this.onStreamRemovedCallbacks.push(callback);
  }

  destroy() {
    if (this.janus) {
      this.janus.destroy();
    }
  }
}

export default JanusVideoRoomClient;
