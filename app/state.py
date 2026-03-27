"""
Shared application state.

These are the global variables that cross view boundaries:
  - result : login row tuple (username, email, password, role)
  - mode   : 1 = dark dashboard, 2 = light dashboard
  - vid    : active cv2.VideoCapture instance (released on camera stop)
"""

result = None
mode = None
vid = None
