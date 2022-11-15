#!/usr/bin/env python3
import time
#from face recognition
from mtcnn.src import detect_faces, show_bboxes
from ArcFace.mobile_model import mobileFaceNet
from util_face_recognition import cosin_metric, get_feature, draw_ch_zn
import os
from torchvision import transforms
from PIL import Image,ImageFont,ImageDraw
#from yolov3
import time
from util_people_detection import *
from darknet import Darknet
import random
import pickle as pkl
#from Kalman filter
from kalman_filter.tracker import Tracker
import imutils
import argparse
from imutils.video import VideoStream
from db_firebase import update_metadata_firebase

sep = os.sep

#parameters from face recognition
font = ImageFont.truetype('simhei.ttf',20,encoding='utf-8')
cfgfile = "cfg/yolov3.cfg"
#cfgfile = "cfg/yolo-fastest.cfg"
weightsfile ="model_data/yolov3.weights"
#weightsfile ="model_data/yolo-fastest.weights"
num_classes = 1
#parameters from people detection
classes = load_classes('data/voc.names')
#classes = load_classes('data/coco.names')

#parameters for Kalman Filter


#functions from yolov3
def prep_image(img, inp_dim):
    """
    Prepare image for inputting to the neural network. 
    
    Returns a Variable 

    img_是适配后的图像
    orig_im是原始图像
    """

    orig_im = img
    dim = orig_im.shape[1], orig_im.shape[0]
    img = cv2.resize(orig_im, (inp_dim, inp_dim))
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim

def get_test_input(input_dim, CUDA):
    img = cv2.imread("imgs/messi.jpg")
    img = cv2.resize(img, (input_dim, input_dim)) 
    img_ =  img[:,:,::-1].transpose((2,0,1))
    img_ = img_[np.newaxis,:,:,:]/255.0
    img_ = torch.from_numpy(img_).float()
    img_ = Variable(img_)
    
    if CUDA:
        img_ = img_.cuda()
    
    return img_

def write(x, img):
    c1 = tuple(x[1:3].astype(int))
    c2 = tuple(x[3:5].astype(int))
    cls = int(x[-1])
    label = "{0}".format(classes[cls])
    color = (255,0,0)
    cv2.rectangle(img, c1, c2,color, 1)
    t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
    c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
    cv2.rectangle(img, c1, c2,color, -1)
    cv2.putText(img, label, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1)

    cv2.line(img, (400, 0), (400, 800), (0, 255, 255), 2)
    #cv2.line(img, (int(c1[0]), 0), (int(c1[0]), 800), (0, 255, 255), 2)
    return img

def sellect_person(output):
    '''
    筛选output，只有标签为person的才被保留
    '''
    result = []
    for i in output:
        if i[-1] == 0:
            result.append(i)
    return result

def to_xy(outputs):
    '''
    把output的格式变为2X1X人物数的多维矩阵
    x,y为框的中心点
    '''
    output_xy = []
    for output in outputs:
        x = 0.5*(output[1] + output[3])
        y = 0.5*(output[2] + output[4])
        output_xy.append([[x],[y]])
    return output_xy

def xy_to_normal(outputs,tracks):
    '''
    中心点位置更新过后，将其换回原来的数据形式
    '''
    output_normal = []
    i = 0
    for output in outputs:
        x_l = int(tracks[i].prediction[0] - 0.5*(output[3]-output[1]))
        y_l = int(tracks[i].prediction[1] - 0.5*(output[4]-output[2]))
        x_r = int(tracks[i].prediction[0] + 0.5*(output[3]-output[1]))
        y_r = int(tracks[i].prediction[1] + 0.5*(output[4]-output[2]))
        id = tracks[i].track_id
        output_normal.append([x_l,y_l,x_r,y_r,id])
        i+=1
    return output_normal


def get_person_position(kalman_output, dist_info):
    position_x = 0.5*(kalman_output[0] + kalman_output[2])
    position_y = 0.5*(kalman_output[1] + kalman_output[3])
    return [position_x, position_y, dist_info]

def calculate_position_diff(person_position, desired_dist = 1.0):
    diff_x = 0.001*person_position[2]*(320 - person_position[0])
    diff_z = person_position[2] - desired_dist
    diff_ang = np.arctan(diff_x/person_position[2])
    return [diff_x, diff_z,diff_ang]

  #  if diff_x  < 400:
#    recognize_frame, name_person = recognize(frame)
#	time_stamp = str(time.time()).replace('.', '_')
#	img_path_local = r'output' + sep + 'images' + sep + name_person + '_' + time_stamp + '.png'
#	cv2.imwrite(img_path_local, recognize_frame)
#	update_metadata_firebase(img_path_local, name_person)

'''
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# Start streaming
profile = pipeline.start(config)
'''
def main():
##########################################################################################################
    #preparation part
    confidence = float(0.25)
    nms_thesh = float(0.4)
    start = 0
    CUDA = torch.cuda.is_available()
    
    num_classes = 80
    
    model = Darknet(cfgfile)
    model.load_weights(weightsfile)
    
    model.net_info["height"] =  "160"
    inp_dim = int(model.net_info["height"])
    
    assert inp_dim % 32 == 0                   #assert后面语句为false时触发，中断程序
    assert inp_dim > 32
    
    if CUDA:
        model.cuda()
   
    model.eval()

    #Kalman Filter
    tracker = Tracker(dist_thresh = 160, max_frames_to_skip = 100, 
                                        max_trace_length = 5, trackIdCount = 1)
    
    global confirm
    global person
    
    fps = 0.0
    count = 0
    frame = 0

    person = []
    confirm = False
    reconfirm = False
    count_yolo = 0
    '''
    #record the video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output/testwrite_normal.avi',fourcc, 15.0, (640,480),True)
    '''



    cap = cv2.VideoCapture(0)

    #vs = VideoStream(src=0).start()
    #time.sleep(2.0)
    #W = None
    #H = None
    #Tframe = vs.read()
    #Tframe = imutils.resize(Tframe, width=500)
    #if W is None or H is None:
    #(H, W) = Tframe.shape[:2]


    detect_time = []
    recogn_time = []
    kalman_time = []
    aux_time = []
    while True:
        start = time.time()  
        ret, color_image = cap.read()


        '''
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        '''
        if color_image is None:
            break

        img, orig_im, dim = prep_image(color_image, inp_dim)
        
        im_dim = torch.FloatTensor(dim).repeat(1,2)  
                
##################################################################################################
        #people detection part                
        if CUDA:
            im_dim = im_dim.cuda()
            img = img.cuda()

        time_a = time.time()
        if count_yolo %3 ==0:
            output = model(Variable(img), CUDA)                         #适配后的图像放进yolo网络中，得到检测的结果
            output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)         


            if type(output) == int:
                fps  = ( fps + (1./(time.time()-start)) ) / 2
                print("fps= %f"%(fps))
                cv2.imshow("frame", orig_im)
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    break
                continue
        
            output[:,1:5] = torch.clamp(output[:,1:5], 0.0, float(inp_dim))/inp_dim                #夹紧张量，限制在一个区间内
        
            #im_dim = im_dim.repeat(output.size(0), 1)
            output[:,[1,3]] *= color_image.shape[1]
            output[:,[2,4]] *= color_image.shape[0]
            output = output.cpu().numpy() 
            output = sellect_person(output)                                       #把标签不是人的output去掉，减少计算量
            output = np.array(output)

            output_update = output
        elif count_yolo %3 != 0:
            output = output_update
        count_yolo += 1
        list(map(lambda x: write(x, orig_im), output))                #把结果加到原来的图像中   
        #output的[0,1:4]分别为框的左上和右下的点的位置
        detect_time.append(time.time() - time_a)
###########################################################################################################
        #kalman filter tracking part
        time_a = time.time()
        output_kalman_xywh = to_xy(output)                   #把output数据变成适合kalman更新的类型
        if (len(output_kalman_xywh) > 0):
            tracker.Update(output_kalman_xywh)                #用kalman filter更新框的位置
        
        outputs_kalman_normal = np.array(xy_to_normal(output,tracker.tracks)) #换回原来的数据形式
        #画框
        for output_kalman_normal in outputs_kalman_normal:
            cv2.rectangle(orig_im, (int(output_kalman_normal[0]), int(output_kalman_normal[1])), 
                                        (int(output_kalman_normal[2]), int(output_kalman_normal[3])),(255,255,255), 2)
            cv2.putText(orig_im, str(output_kalman_normal[4]),(int(output_kalman_normal[0]), int(output_kalman_normal[1])),
                                    0, 5e-3 * 200, (0,255,0),2)



            #track id 就是数字
        kalman_time.append(time.time() - time_a)
#tracker.tracks[i].track_id
########################################################################################################
        #face recognition part
        time_a = time.time()
        if confirm == False:

            saved_model = './ArcFace/model/068.pth'
            name_list = os.listdir('./users')
            path_list = [os.path.join('./users',i,'%s.txt'%(i)) for i in name_list]
            total_features = np.empty((128,),np.float32)

            for i in path_list:
                temp = np.loadtxt(i)
                total_features = np.vstack((total_features,temp))
            total_features = total_features[1:]

            #threshold = 0.30896     #阈值并不合适，可能是因为训练集和测试集的差异所致！！！
            threshold = 0.5
            model_facenet = mobileFaceNet()
            model_facenet.load_state_dict(torch.load(saved_model, map_location=torch.device('cpu'))['backbone_net_list'])
            model_facenet.eval()
            #use_cuda = torch.cuda.is_available() and True
            #device = torch.device("cuda" if use_cuda else "cpu")
            device = torch.device('cpu')
            #map_location=torch.device('cpu')

            # is_cuda_avilable
            trans = transforms.Compose([
                transforms.Resize((112,112)),
                transforms.ToTensor(),
                transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5])
            ])
            model_facenet.to(device)

            img = Image.fromarray(color_image)
            bboxes, landmark = detect_faces(img)                                                                  #首先检测脸

            if len(bboxes) == 0:
                print('detect no people')
            else:
                for bbox in bboxes:
                    print(bbox[:4])
                    loc_x_y = [bbox[2], bbox[1]]
                    person_img = color_image[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])].copy()              #从图像中截取框
                    feature = np.squeeze(get_feature(person_img, model_facenet, trans, device))                               #框里的图像计算feature
                    cos_distance = cosin_metric(total_features, feature)
                    index = np.argmax(cos_distance)
                    if  cos_distance[index] <= threshold:
                        continue
                    person = name_list[index]  
                    #在这里加框加文字
                    orig_im = draw_ch_zn(orig_im,person,font,loc_x_y)                                                                    #加名字
                    cv2.rectangle(orig_im,(int(bbox[0]),int(bbox[1])),(int(bbox[2]),int(bbox[3])),(0,0,255))           #加box
            #cv2.imshow("frame", orig_im)

############################################################################################################
            #confirmpart
            print('confirmation rate: {} %'.format(count*10))
            cv2.putText(orig_im, 'confirmation rate: {} %'.format(count*10), (10,30),cv2.FONT_HERSHEY_PLAIN, 2, [0,255,0], 2)
            if len(bboxes)!=0 and len(output)!=0:
                if bboxes[0,0]>output[0,1] and bboxes[0,1]>output[0,2] and bboxes[0,2]<output[0,3] and bboxes[0,3]<output[0,4] and person:
                    count+=1
                frame+=1
            if count>=10 and frame<=30:
                confirm = True
                print('confirm the face is belong to that people')
            elif  frame >= 30:
                print('fail confirm, and start again')
                reconfirm = True
                count = 0
                frame = 0
            if reconfirm == True:
                cv2.putText(orig_im, 'fail confirm, and start again', (10,60),cv2.FONT_HERSHEY_PLAIN, 2, [0,255,0], 2)      
        recogn_time.append(time.time() - time_a)             

###############################################################################################################
        time_a = time.time()
        #show the final output result
        if not confirm:
            cv2.putText(orig_im, 'still not confirm', (output[0,1].astype(np.int32)+100,output[0,2].astype(np.int32)+20),
                                     cv2.FONT_HERSHEY_PLAIN, 2, [0,0,255], 2)
        if confirm:
            for output_kalman_normal in outputs_kalman_normal:
                if output_kalman_normal[4] == 1:
                    cv2.putText(orig_im, person, (output_kalman_normal[0].astype(np.int32)+100,output_kalman_normal[1].astype(np.int32)+20),
                                            cv2.FONT_HERSHEY_PLAIN, 2, [0,255,0], 2)
                    
                    #dist_info = get_dist_info(depth_image,bbox)                   #深度信息z
                    
                    #orig_im = add_dist_info(orig_im,bbox,dist_info)



        cv2.imshow("frame", orig_im)


        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

        aux_time.append(time.time()-time_a)
        fps  = ( fps + (1./(time.time()-start)) ) / 2
        print("fps= %f"%(fps))
    
    avg_detect_time = np.mean(detect_time)
    avg_recogn_time = np.mean(recogn_time)
    avg_kalman_time = np.mean(kalman_time)
    avg_aux_time = np.mean(aux_time)
    print("avg detect: {}".format(avg_detect_time))
    print("avg recogn: {}".format(avg_recogn_time))
    print("avg kalman: {}".format(avg_kalman_time))
    print("avg aux: {}".format(avg_aux_time))
    print("avg fps: {}".format(1/(avg_detect_time + avg_recogn_time + avg_kalman_time + avg_aux_time)))

    cv2.destroyAllWindows()


if __name__ =='__main__':
    main()
