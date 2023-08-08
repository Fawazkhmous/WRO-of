import cv2
import time
import cvzone
import YB_Pcb_Car
from cvzone.ColorModule import ColorFinder


def CTime(Time, Type=None):

    if  Time >= 1.5: TurnTime = 2
    elif 1.5 >= Time >= 0.8: TurnTime = 1.88
    else: TurnTime = 1.7

    if Type == 'dist': return (Time * 6) / TurnTime

    Time = ((1 - (Time / TurnTime)) * 6) / 0.5
    if Time <= 0: return 0.2

    return Time * 0.2


cap = cv2.VideoCapture(0)
color_finder = ColorFinder()
car = YB_Pcb_Car.YB_Pcb_Car()

Blue = {'hmin': 95, 'smin': 80, 'vmin': 0, 'hmax': 125, 'smax': 255, 'vmax': 255}
Orange = {'hmin': 0, 'smin': 170, 'vmin': 0, 'hmax': 20, 'smax': 255, 'vmax': 255}

Blue_Flage, Orange_Flage, Turn = False, False, False

Straight, Left, Right = 93, 63, 123
LineCounter, NumOfLines = 0, 12

car.Ctrl_Servo(1, Straight)
time.sleep(0.3)

stfd = time.time()

while True:
    try:
        img = cap.read()[1][180: 300, 250: 390]

        BlueColor = cvzone.findContours(img, (color_finder.update(img, Blue)[1]), 3000)[1]

        OrangeColor = cvzone.findContours(img, (color_finder.update(img, Orange)[1]), 2000)[1]


        if BlueColor and Orange_Flage is False and Turn is False:
            Direction = Left
            Turn, Blue_Flage = True, True
            LineCounter += 1

            stft = time.time()


        elif OrangeColor and Blue_Flage is False and Turn is False:
            Direction = Right
            Turn, Orange_Flage = True, True
            LineCounter += 1

            stft = time.time()


        elif Turn:
            car.Ctrl_Servo(1,  Direction)

            if Direction == Left and OrangeColor:
                print(time.time() - stft)
                time.sleep(CTime(time.time() - stft))
                car.Ctrl_Servo(1, Straight)
                Turn = False


            elif Direction == Right and BlueColor:
                time.sleep(CTime(time.time() - stft))
                car.Ctrl_Servo(1, Straight)
                Turn = False

            if LineCounter == 1: 
                DriveTime = CTime(time.time() - stft, 'dist') - (time.time() - stfd)
            
            elif LineCounter == NumOfLines and Turn is False:
                car.Ctrl_Servo(1,  Straight)
                car.Car_Run(100, 100)
                time.sleep(DriveTime if DriveTime > 0.5 else 1)
                break

        else: 
            car.Car_Run(100, 100)
            car.Ctrl_Servo(1,  Straight)
        

        cv2.imshow('img', img)
        if cv2.waitKey(1) & 0xff == 27: break   

    except Exception as error: print(error.with_traceback()) ; break

car.Car_Stop()
car.Ctrl_Servo(1, Straight)
del car
