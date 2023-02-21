import cv2 
import numpy as np
import glob # 특정 확장자 파일들 리스트로 다루기
import os

# 동일 이미지 크기 지정
img_W = 1280
img_H = 720
##img_W = 1920 #유튜브 권장 해상도?
##img_H = 1080
t_size = (img_W, img_H)

def make(directory) :
    # 한글파일명/경로 img 파일 읽어 이미지들 크기 동일하게 조절하여 저장
    jpgname = directory + '*.jpg'
    print(jpgname)
    for i, filename in enumerate(glob.glob(jpgname)):        
        print(filename)
        img_array = np.fromfile(filename, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        height, width, layers = img.shape
        print('W:', width, ', H:', height)
        resized_img = cv2.resize(img, t_size, interpolation= cv2.INTER_LINEAR)

        num_str = str(i).zfill(2) # 0으로 채워진 문자열 만들기
        cv2.imwrite(num_str+'.jpg', resized_img)


    # 위 동일크기 이미지들 합쳐 동영상 파일 만들기
    img_array = []
    for filename in glob.glob('*.jpg'):
        img = cv2.imread(filename)
        for i in range(150):
            img_array.append(img)

    fps = 0.3 # 초당 frame수
    # 비디오 write option DIVX, MJPG, XVID, FMP4, X264
    out = cv2.VideoWriter(directory+'marketingvideo.avi',cv2.VideoWriter_fourcc(*'DIVX'), 5, t_size) #MJPG 0.33
    for i in range(len(img_array)):
        out.write(img_array[i])
    # os.remove('00.jpg')
    # os.remove('01.jpg')
    out.release()

for cnt in range(18):
    print(str(cnt+3171))
    make('C:\\coding\\detail_page\\'+str(cnt+3171)+'\\')


#https://blog.naver.com/kkang2yah/222797796995