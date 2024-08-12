import asyncio
from janus_client import JanusSession, JanusVideoRoomPlugin

from aiortc import VideoStreamTrack
from aiortc.contrib.media import MediaRelay, MediaPlayer
from av import VideoFrame
import numpy as np
import cv2
import logging
import os
from core.settings import setting

JANUS_URL = setting.MEDIA_SERVER #"ws://localhost:8188"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CameraStreamer(VideoStreamTrack):
    def __init__(self, stream_source=0):
        super().__init__()
        self.cap = cv2.VideoCapture(stream_source)
        if not self.cap.isOpened():
            raise ValueError("Could not open video source")
        self.frame_rate = 30

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()

        if not ret:
            # If we can't receive frame, we'll send a blank frame
            frame = np.zeros((400, 460, 3), dtype=np.unit8)

        # Convert frame to RGB (required format for VideoFrame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create VideoFrame
        video_frame = VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        return video_frame

    def stop(self):
        if self.cap is not None:
            self.cap.release()


class StreamServiveRunner:
    def __init__(self, source, room_id, stream_name):
        self.room_id = int(room_id)
        self.stream_name = stream_name
        self.source = int(source) # to change later
        print("Args SERVICERUNNER :",self.room_id, self.stream_name, self.source)
        # Janus
        self.session = JanusSession(base_url=JANUS_URL)
        self.plugin = JanusVideoRoomPlugin()
        self.relay = MediaRelay()

    async def start(self):
        track = None
        try:
            # Attach plugin here
            await self.plugin.attach(session=self.session)
            # await self.plugin.start()

            # Join room
            join_res = await self.plugin.join(room_id=self.room_id, display_name=self.stream_name)
            print("Join response :", join_res)

            # checking for either media player or camear source 
            # track = None
            # if self.source != 0:
            #     player = MediaPlayer(self.source)
            #     video_track = player.video
            #     track = self.relay.subscribe(video_track)
            # else:
            #     track = CameraStreamer(self.source)
            track = CameraStreamer(self.source)
            #configuration
            configuration = {}
            publish_res = await self.plugin.publish([track], configuration)
            print("Publish Results: %s", publish_res)
        
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print("Exception :", e)
        finally:
            #clean up
            if track is not None:
                track.stop()
            if 'plugin_handle' in locals():
                await self.plugin.unpublish()
            if 'session' in locals():
                await self.session.destroy()
