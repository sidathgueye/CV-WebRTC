import asyncio
import json
import math
import cv2
import numpy
import socketio
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, RTCIceServer, RTCConfiguration, \
    VideoStreamTrack, sdp
from aiortc.contrib.media import MediaPlayer


STUN_SERVER = ("stun.l.google.com", 19302)
SOCKET_URI = "https://api5.securemotion.fr:9000/"
#SOCKET_URI = "http://192.168.0.41:9000/"
sio = socketio.AsyncClient()
room = 'foo'
isChannelReady = False
isInitiator = False
isStarted = False
pc = RTCPeerConnection()


class FlagVideoStreamTrack(VideoStreamTrack):
    """
    A video track that returns an animated flag.
    """

    def __init__(self):
        super().__init__()  # don't forget this!
        self.counter = 0
        height, width = 480, 640

        # generate flag
        data_bgr = numpy.hstack(
            [
                self._create_rectangle(
                    width=213, height=480, color=(255, 0, 0)
                ),  # blue
                self._create_rectangle(
                    width=214, height=480, color=(255, 255, 255)
                ),  # white
                self._create_rectangle(width=213, height=480, color=(0, 0, 255)),  # red
            ]
        )

        # shrink and center it
        M = numpy.float32([[0.5, 0, width / 4], [0, 0.5, height / 4]])
        data_bgr = cv2.warpAffine(data_bgr, M, (width, height))

        # compute animation
        omega = 2 * math.pi / height
        id_x = numpy.tile(numpy.array(range(width), dtype=numpy.float32), (height, 1))
        id_y = numpy.tile(
            numpy.array(range(height), dtype=numpy.float32), (width, 1)
        ).transpose()

        self.frames = []
        # for k in range(30):
        #     phase = 2 * k * math.pi / 30
        #     map_x = id_x + 10 * numpy.cos(omega * id_x + phase)
        #     map_y = id_y + 10 * numpy.sin(omega * id_x + phase)
        #     self.frames.append(
        #         av.VideoFrame.from_ndarray(
        #             cv2.remap(data_bgr, map_x, map_y, cv2.INTER_LINEAR), format="bgr24"
        #         )
        #     )

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = self.frames[self.counter % 30]
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame

    def _create_rectangle(self, width, height, color):
        data_bgr = numpy.zeros((height, width, 3), numpy.uint8)
        data_bgr[:, :] = color
        return data_bgr


@sio.event
async def connect():
    await sio.emit('connect')
    print('connection established')


@sio.event
async def created(room):
    print('created room ' + room)
    isInitiator = True


@sio.event
async def full(room):
    print('Room : ' + room + ' is full')


@sio.event
async def join(room):
    print('Another peer made a request to join room : ' + room)
    print('This peer is the initiator of room ' + room)
    isChannelReady = True


@sio.event
async def joined(room):
    print('joined ' + room)
    isChannelReady = True


@sio.event
async def disconnect():
    print('disconnected from server')


@sio.event
async def message(message):
    if message == 'got user media':
        pc.addTransceiver("video", direction="recvonly")
        pc.addTransceiver("audio", direction="recvonly")
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        print(offer.sdp + "\n")
        mes_json = json.dumps({"type": offer.type, "sdp": pc.localDescription.sdp})
        json_obj = json.loads(mes_json)
        await sio.emit('message', json_obj)
        await sio.wait()
    print('mes : ' + str(message))

# def maybeStart():
#     print('maybeStart ' + str(isStarted) + ' ' + str(isChannelReady))
#     if isStarted == False and isChannelReady:
#         createPeerConnection()
#         isStarted = True
#         if isInitiator:
#             doCall()


async def run(pc):
    await sio.connect(SOCKET_URI)
    if room != '':
        await sio.emit('create or join', room)
        print('Attempted to create or join room : ' + room)
    player = MediaPlayer('/home/gael/Desktop/darknet_detection/Big_Buck_Bunny_1080_10s_1MB.mp4')
    pc.addTrack(player.video)
    #pc.addTrack(player.audio)
    await sio.wait()


def createPeerConnection():

    @pc.on("connectionstatechange")
    def connectionstatechange():
        print("connectionState " + pc.connectionState)

    @pc.on("iceconnectionstatechange")
    def iceconnectionstatechange():
        print("iceConnectionStat " + pc.iceConnectionState)

    @pc.on("icegatheringstatechange")
    def icegatheringstatechange():
        print("iceGatheringState " + pc.iceGatheringState)

    @pc.on("signalingstatechange")
    def signalingstatechange():
        print("signalingstatechange " + pc.signalingState)


# async def main():
#     await sio.connect(SOCKET_URI)
#     await sio.wait()
#     if room != '':
#         await sio.emit('create or join', room)
#         print('Attempted to create or join room : ' + room)


if __name__ == '__main__':
    iceServers = RTCIceServer(urls='stun:stun.l.google.com:19302')
    pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=[iceServers]))

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(pc=pc))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
