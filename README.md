# CV-WebRTC

In this project the objective is to set up a connection between two clients who connect to a web server and who send video streams to each other.

However, we have a java client (android project located at this link: https: //github.com/IhorKlimov/Android-WebRtc.git). 
This Java client manages to connect and send the video stream from his camera.

The other client which is written in python, it manages to connect but does not send a video stream.
the error opposite is returned:


```
 Traceback (most recent call last):
  File "/home/gael/.local/lib/python3.9/site-packages/socketio/asyncio_client.py", line 465, in _handle_eio_message
    await self._handle_event (pkt.namespace, pkt.id, pkt.data)
  File "/home/gael/.local/lib/python3.9/site-packages/socketio/asyncio_client.py", line 335, in _handle_event
    r = await self._trigger_event (data [0], namespace, * data [1:])
  File "/home/gael/.local/lib/python3.9/site-packages/socketio/asyncio_client.py", line 391, in _trigger_event
    ret = await self.handlers [namespace] [event] (* args)
  File "/home/gael/darknet_detection/webrtc-cli.py", line 133, in message
    await pc.setRemoteDescription (sdp)
  File "/home/gael/.local/lib/python3.9/site-packages/aiortc/rtcpeerconnection.py", line 799, in setRemoteDescription
    description = sdp.SessionDescription.parse (sessionDescription.sdp)
AttributeError: 'str' object has no attribute 'sdp'


```

NB: The connection is well established and data is exchanged, we just can't see the videos.

The URLs in the code correspond to the servers used.
