import cv2
import time
import mediapipe as mp
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy

earlier=0
cap=cv2.VideoCapture(0)
status="off"
a=0
b,g,r=255,100,0

#setting up mediapipe
mphands=mp.solutions.hands
Hands=mphands.Hands(min_detection_confidence=0.7)  #min_detection_confidence=0.5  (optional parameter)
mpdraw=mp.solutions.drawing_utils

# setting up pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
Vol=0

while True:
    cords=[]
    Time=time.time()
    a=1/(Time - earlier)
    earlier=Time
    fingers=0
    _,frame=cap.read()
    img=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results=Hands.process(img)
    
    if results.multi_hand_landmarks:
        for hand_in_frame in results.multi_hand_landmarks:
            for id,lm in enumerate(hand_in_frame.landmark): #id will give x,y,z of lm i.e. landmark for eg lm=0-20
                h,w,c=img.shape                              # size of frame
                cx,cy=int(lm.x*w),int(lm.y*h)                 # getting co ordinates of all landmarks
                position=[cx,cy]
                cords.append(position)
            '''
            # counts the no of fingers    
            if cords[8][1]<cords[6][1]:
                fingers+=1
            if cords[12][1]<cords[10][1]:
                fingers+=1
            if cords[16][1]<cords[14][1]:       # origin in top left/x,y increase towards bottom right
                fingers+=1
            if cords[20][1]<cords[18][1]:
                fingers+=1
            if cords[4][1]<cords[3][1]:
                fingers+=1
            cv2.putText(frame,"Fingers up:"+str(fingers),(400,30),cv2.FONT_HERSHEY_PLAIN,2,(255,100,0),2)
            '''

            mpdraw.draw_landmarks(frame,hand_in_frame,mphands.HAND_CONNECTIONS)
        cv2.circle(frame,(cords[4][0],cords[4][1]),15,(255,100,0),cv2.FILLED)  #gets thumb
        cv2.circle(frame,(cords[8][0],cords[8][1]),15,(255,100,0),cv2.FILLED) #gets index finger
        ax,ay=(cords[4][0]+cords[8][0])//2,(cords[4][1]+cords[8][1])//2   #gets the  cords ofmidpoint of the line
        
        cv2.line(frame,(cords[8][0],cords[8][1]),(cords[4][0],cords[4][1]),(255,100,0),5) # gets line
        cv2.circle(frame,(ax,ay),15,(255,100,0),cv2.FILLED)      #gets mid point
        length=math.hypot(cords[8][0]-cords[4][0],cords[8][1]-cords[4][1])    #gets length of line
        cv2.putText(frame,"length"+str(length),(400,30),cv2.FONT_HERSHEY_PLAIN,2,(255,100,0),2)    # gets length of line
        
        volrange=volume.GetVolumeRange()   #volume range is from -65.25 to 0
        
        #print(vol)
               
               #changes volume to percentage
        cv2.putText(frame,"Volume"+str(int(Vol))+"%",(400,60),cv2.FONT_HERSHEY_PLAIN,2,(255,100,0),2)    # gets percentage
        if status=='on':
            vol=numpy.interp(length,[30,250],[volrange[0],volrange[1]])  #hand range 50---270 vol range -65--0
            volume.SetMasterVolumeLevel(vol, None)          # sets volume
            Vol=numpy.interp(length,[30,250],[0,100])


        if int(Vol)>=80:            # 80% safty
            cv2.circle(frame,(ax,ay),15,(0,0,255),cv2.FILLED)
            cv2.putText(frame,"Volume"+str(int(Vol))+"%",(400,60),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255),2)
            
        if cords[20][1]>cords[17][1]  and status=='on'and a:
            status="off"
            a=False
            time.sleep(0.5)
            b,g,r=255,100,0
        
            
        elif cords[20][1]>cords[17][1] and status=='off' and a:
            status="on"
            a=False
            time.sleep(0.5)
            b,g,r=0,0,255
            

        if cords[20][1]<cords[17][1]:
            
            a=True
        
        #print(status)
        cv2.putText(frame,"Status:"+status,(10,60),cv2.FONT_HERSHEY_PLAIN,2,(b,g,r),2)

    cv2.putText(frame,"Frame Rate:"+str(int(a)),(10,30),cv2.FONT_HERSHEY_PLAIN,2,(255,100,0),2)
    cv2.imshow('frame',frame)
    k=cv2.waitKey(30) & 0xff
    if k==27:
        break

cap.release()





















