import sys
import struct
import time
from Quartz.CoreGraphics import CGEventCreateMouseEvent
from Quartz.CoreGraphics import CGEventSetDoubleValueField
from Quartz.CoreGraphics import CGEventPost
from Quartz.CoreGraphics import CGRectMake
from Quartz.CoreGraphics import CGDisplayBounds
from Quartz.CoreGraphics import CGGetActiveDisplayList
from Quartz.CoreGraphics import kCGEventMouseMoved
from Quartz.CoreGraphics import kCGEventLeftMouseDown
from Quartz.CoreGraphics import kCGEventLeftMouseUp
from Quartz.CoreGraphics import kCGEventRightMouseDown
from Quartz.CoreGraphics import kCGEventRightMouseUp
from Quartz.CoreGraphics import kCGMouseButtonLeft
from Quartz.CoreGraphics import kCGTabletEventPointPressure
from Quartz.CoreGraphics import kCGMouseEventPressure
from Quartz.CoreGraphics import kCGEventTabletPointer
from Quartz.CoreGraphics import kCGEventTabletProximity
from Quartz.CoreGraphics import kCGHIDEventTap
from Quartz.CoreGraphics import CGEventSetLocation
from Quartz.CoreGraphics import CGEventSetType
from Quartz.CoreGraphics import CGEventSetIntegerValueField
from Quartz.CoreGraphics import kCGMouseEventSubtype
from Quartz.CoreGraphics import kCGTabletEventPointButtons
from Quartz.CoreGraphics import kCGEventMouseSubtypeTabletPoint
from Quartz.CoreGraphics import CGEventCreate
from Quartz.CoreGraphics import CGPointMake
from Quartz.CoreGraphics import kCGTabletEventPointX
from Quartz.CoreGraphics import kCGTabletEventPointY
from Quartz.CoreGraphics import kCGTabletEventTiltX
from Quartz.CoreGraphics import kCGTabletEventTiltY
from Quartz.CoreGraphics import kCGTabletEventDeviceID
from Quartz.CoreGraphics import kCGTabletEventPointZ
from Quartz.CoreGraphics import kCGTabletEventRotation
from Quartz.CoreGraphics import kCGTabletEventTangentialPressure
import socket

def UpdateDisplaysBounds():
        screenBounds = CGRectMake(0.0, 0.0, 0.0, 0.0)
        err, ids, count = CGGetActiveDisplayList(10, None, None)
        screenBounds = CGDisplayBounds(ids[0])
        return screenBounds

def mouseEvent(type, posx, posy, pressure,whichbutton,status):
        theEvent = CGEventCreateMouseEvent(None,type,(posx,posy),kCGMouseButtonLeft)
        #CGEventSetType(theEvent,type)
        #CGEventSetLocation(theEvent,(posx,posy))

        CGEventSetIntegerValueField(theEvent,kCGMouseEventSubtype,kCGEventMouseSubtypeTabletPoint)

        CGEventSetIntegerValueField(theEvent, kCGTabletEventPointX, posx);
        CGEventSetIntegerValueField(theEvent, kCGTabletEventPointY, posy);

        CGEventSetDoubleValueField(theEvent, kCGMouseEventPressure, pressure);
        CGEventSetDoubleValueField(theEvent, kCGTabletEventPointPressure, pressure);

        CGEventSetDoubleValueField(theEvent, kCGTabletEventTiltX, 0);
        CGEventSetDoubleValueField(theEvent, kCGTabletEventTiltY, 0);

        CGEventSetIntegerValueField(theEvent, kCGTabletEventDeviceID, 0);
        CGEventSetIntegerValueField(theEvent, kCGTabletEventPointZ, 0);
        CGEventSetDoubleValueField(theEvent, kCGTabletEventRotation, 0);
        CGEventSetDoubleValueField(theEvent, kCGTabletEventTangentialPressure, 0);

        #CGEventSetLocation(theEvent,(posx,posy))

        if(whichbutton==0&status==0):
          buttonstatuses = buttonstats & 0x10
        elif(whichbutton==0&status==1):
          buttonstatuses = buttonstats | 0x01
        if(whichbutton==1&status==0):
          buttonstatuses = buttonstats & 0x01
        elif(whichbutton==1&status==1):
          buttonstatuses = buttonstats | 0x10

        CGEventSetIntegerValueField(theEvent,kCGTabletEventPointButtons,buttonstatuses)

        CGEventPost(kCGHIDEventTap, theEvent)
        return buttonstatuses

def mousemove(posx,posy,pressure,status):
        buttonstatuses = mouseEvent(kCGEventMouseMoved, posx,posy,pressure, buttonnum,status);
        #if(buttonnum==0):
        #    buttonstatuses = mouseEvent(kCGEventLeftMouseDown, posx,posy,pressure, buttonnum,buttonstatus);
        #else:
        #    buttonstatuses = mouseEvent(kCGEventRightMouseDown, posx,posy,pressure, buttonnum,buttonstatus);
def mouseclick(posx,posy, pressure,whichbutton,status):
        if(status==1):
                if(buttonnum==0):
                        buttonstats = mouseEvent(kCGEventLeftMouseDown, posx,posy,pressure,whichbutton,status)
                        print "pen down"
                elif(buttonnum==1):
                        buttonstats = mouseEvent(kCGEventRightMouseDown, posx,posy,pressure,whichbutton,status)
                        print "eraser down"
        elif(status==0):
                if(buttonnum==0):
                        buttonstats = mouseEvent(kCGEventLeftMouseUp, posx,posy,pressure,whichbutton,status)
                        print "pen up"
                elif(buttonnum==1):
                        buttonstats = mouseEvent(kCGEventRightMouseUp, posx,posy,pressure,whichbutton,status)
                        print "eraser up"     

rect = UpdateDisplaysBounds()
gfxTablet= None
version= None
messagetype= None
x= None
y= None
pressure= None
buttonnum= None
buttonstatus = None
buttonstats = 0x00
#print rect

port = 40118        # port where we expect to get a msg

# Create port to listen upon
# --------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.bind(('', port))
except:
    print 'failure to bind'
    s.close()
    raise
    s.setblocking(0)

while True:
     data, addr = s.recvfrom(1024) # buffer size is 1024 bytes
     #print struct.unpack("=9sHHH",data)
     if (data.__len__()==18):
        gfxTablet, version, messagetype, x, y, pressure = struct.unpack(">9sHbHHH",data[0:18])
     elif (data.__len__()==20):
        gfxTablet, version, messagetype, x, y, pressure, buttonnum, buttonstatus = struct.unpack(">9sHbHHHbb",data[0:20])

    # print data.__len__()
    # print  gfxTablet, version, messagetype, x, y, pressure
     if(messagetype==0):
      #  print "move"
        mousemove(x/65535.0*2.0*rect.size.width, (y/65535.0*2.0)*rect.size.height, pressure/19817.0,buttonstatus);
        print x/65535.0*2.0*rect.size.width, (y/65535.0*2.0)*rect.size.height, pressure/19817.0
     elif(messagetype==1):
    #    print "button"
   #     print buttonnum
        #if(buttonstatus ==0):
  #          print "up"
        #else: 
  #          print "down"
    # print x/65535.0*2.0*rect.size.width, (y/65535.0*2.0)*rect.size.height

    # print "pressure"
   #  print pressure/19817.0

        mouseclick(x/65535.0*2.0*rect.size.width, (y/65535.0*2.0)*rect.size.height, pressure/19817.0,buttonnum,buttonstatus);
        print x/65535.0*2.0*rect.size.width, (y/65535.0*2.0)*rect.size.height, pressure/19817.0