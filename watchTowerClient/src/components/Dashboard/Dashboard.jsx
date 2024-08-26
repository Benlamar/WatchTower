import React, { useEffect, useState, useRef, useCallback } from "react";
import VideoRoomClient from "../../Service/JanusRoomClient";
import { useSelector } from "react-redux";

const Dashboard = () => {
  const JANUS_URL = "http://localhost:8088/janus";
  const ROOM_ID = 1122;

  const [streams, setStreams] = useState({});
  const videoRoomRef = useRef(null);

  const roomSelector = useSelector((state)=>state.stream.roomid)

  const handleStreamAdded = useCallback((publisherId, mid, stream) => {
    // console.log(`Stream added: publisher ${publisherId}, mid ${mid}`, stream);
    // console.log(`Stream tracks:`, stream.getTracks());
    setStreams((prev) => ({
      ...prev,
      [publisherId]: {
        ...prev[publisherId],
        [mid]: stream,
      },
    }));
  }, []);

  const handleStreamRemoved = useCallback((publisherId, mid) => {
    // console.log(`Stream removed: publisher ${publisherId}, mid ${mid}`);
    setStreams((prev) => {
      const newStreams = { ...prev };
      if (newStreams[publisherId]) {
        delete newStreams[publisherId][mid];
        if (Object.keys(newStreams[publisherId]).length === 0) {
          delete newStreams[publisherId];
        }
      }
      return newStreams;
    });
  }, []);

  const initVideoRoom = useCallback(() => {
    if (videoRoomRef.current) {
      videoRoomRef.current.destroy();
    }

    const videoRoom = new VideoRoomClient(
      JANUS_URL,
      ROOM_ID,
      handleStreamAdded,
      handleStreamRemoved
    );
    videoRoomRef.current = videoRoom;

    videoRoom
      .init()
      .then(() => console.log("VideoRoom initialized"))
      .catch((error) => {
        // console.error("Error initializing VideoRoom:", error);
        // Attempt to reconnect after a delay
        setTimeout(initVideoRoom, 5000);
      });
  }, [handleStreamAdded, handleStreamRemoved]);

  // useEffect(() => {
  //   initVideoRoom();

  //   return () => {
  //     if (videoRoomRef.current) {
  //       videoRoomRef.current.destroy();
  //     }
  //   };
  // }, [initVideoRoom]);

  // Add event listener for online/offline events
  // useEffect(() => {
  //   const handleOnline = () => {
  //     // console.log("Browser is online, attempting to reconnect...");
  //     initVideoRoom();
  //   };

  //   window.addEventListener("online", handleOnline);

  //   return () => {
  //     window.removeEventListener("online", handleOnline);
  //   };
  // }, [initVideoRoom]);

  return (
    <div className="dashboard h-full p-4">
      <h1>Dashboard {roomSelector}</h1>

      <div className="video-container grid grid-cols-2 gap-4">
        {Object.entries(streams).map(([publisherId, publisherStreams]) => (
          <div key={publisherId} className="publisher-container">
            <h2 className="text-lg font-bold mb-2">Publisher {publisherId}</h2>
            <div className="streams-container">
              {Object.entries(publisherStreams).map(([mid, stream]) => {
                return (
                  <div key={mid} className="stream-container mb-2">
                    <p className="text-sm mb-1">Stream {mid}</p>
                    <video
                      className="w-full"
                      autoPlay
                      playsInline
                      muted="muted"
                      ref={(el) => {
                        if (el) {
                          if (el.srcObject !== stream) {
                            el.srcObject = stream;
                          }
                        }
                      }}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
