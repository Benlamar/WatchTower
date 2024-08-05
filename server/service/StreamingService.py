import cv2
import asyncio
import numpy as np

from av import VideoFrame
from aiortc import VideoStreamTrack
from aiortc.contrib.media import MediaRelay, MediaPlayer
from janus_client import JanusSession, JanusVideoRoomPlugin

relay = MediaRelay()

class OpenCVVideoStreamTrack(VideoStreamTrack):
    pass

class StreamRunner:
    pass