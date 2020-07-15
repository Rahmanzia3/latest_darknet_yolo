import os
import wget
import shutil
import requests
import subprocess
from tqdm import tqdm
from zipfile import ZipFile 
from argparse import ArgumentParser
import datetime

import telegram
from telegram.ext import Updater


# Copy reqquire cfg from cfg/ to project directory

'''
This directory should be paced in main folder

'''
def edit_cfg(destination_cfg_dir,classes):
    with open(destination_cfg_dir) as f:
        content = f.readlines()
    '''
    # filters=255
    # classes=80
    # batch = opt.batch_size
    # subdivisions = opt.sub_batch
    Above mentioned values are changed based on argd
    '''
    new_file = []
    for x in content:
        ch_class = x.find('classes=80')
        ch_filter = x.find('filters=255')
        ch_batch = x.find('batch=')
        ch_sub_dic = x.find('subdivisions')
        ch_max_iterations = x.find('max_batches')


        if ch_batch != -1:
            b = 'batch=' +str(opt.batch_size) + '\n'
            new_file.append(b)

        elif ch_sub_dic != -1:
            c = 'subdivisions=' +str(opt.sub_batch) + '\n'
            new_file.append(c)

        elif ch_filter != -1:
            d = 'filters =' +str((classes + 5)*3) + '\n'
            new_file.append(d)

        elif ch_class != -1:
            e = 'classes =' +str(classes) + '\n'
            new_file.append(e)

        elif ch_max_iterations != -1:
            e = 'max_batches = ' +str(opt.epochs) + '\n'
            new_file.append(e)

        else:
            ze = x.find('batch=')
            if ze != -1:
                print('Triggered repeated batch')
            else:
                new_file.append(x)
    empty = open (destination_cfg_dir,'w')
    # empty.writelines('\n')
    empty.close()
    for z in new_file:
        myfile = open(destination_cfg_dir, 'a')
        myfile.writelines(z)

    myfile.close()

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            with tqdm(unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        bar.update(CHUNK_SIZE)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination) 

def un_zip(source,destination):
        file_name = source
      
        # opening the zip file in READ mode 
        with ZipFile(file_name, 'r') as zip: 
        # printing all the contents of the zip file 
            zip.printdir() 
          
            # extracting all the files 
            print('Extracting all the files now...') 

            # ######## ADD DESTINATION LOCATION HERE
            zip.extractall(destination) 
            print('Done!') 

def select_files(path):


    sub_foders = os.listdir(path)
    train = []
    test = []
    names = []
    for x in sub_foders:
        if x == 'test':
            test_dir = os.path.join(path,x)
            test.append(test_dir)
        elif x == 'train':
            train_dir = os.path.join(path,x)
            train.append(train_dir)
        elif x == 'names.txt':
            names_dir = os.path.join(path,x)
            names.append(names_dir)

    return train[0], test[0], names[0]

def create_obj_names(path):
    obj_names_dir = os.path.join(project_dir,'obj.names')
    if_exists = os.path.isfile(obj_names_dir)
    if if_exists is True:
        os.remove(obj_names_dir)
    class_names = []
    file = open(path, 'r')
    lin = file.readlines()
    for x in lin:
        val_name = x.split('\n',1)[0]
        if len(val_name) > 2:
            # print('555555555555555555')
            # print(val_name)
            class_names.append(val_name)
            file_obj_names = open(obj_names_dir,'a')
            file_obj_names.writelines(x)
            file_obj_names.close()


    # Create obj.names in project directory
    # here in OBJ.NAMES we will get one more line after last class
    # If causes more problem write uing another for loop and remove '\n' from last class
    return class_names

def create_txt(path,status):
        '''
        Here this path should consist of xml's as well as .jpg images
        create status.txt in project dir and append all images name their
        '''
        if status == 'test':
            txt_dir = os.path.join(project_dir,'test.txt')
        elif status == 'train':
            txt_dir = os.path.join(project_dir,'train.txt')
        if_exists = os.path.isfile(txt_dir)
        if if_exists is True:
            os.remove(txt_dir)

        sub_images = os.listdir(path)
        count = 0
        for x in sub_images:
            is_jpg = x.rpartition('.')[-1]
            if is_jpg == 'jpg':
                image_dir = os.path.join(path,x)
                print(image_dir)
                count = count + 1
                print(count)
                file_obj_names = open(txt_dir,'a')
                file_obj_names.writelines(image_dir+'\n')
                file_obj_names.close()

def create_obj_data(project_dir,no_class):
        obj_data_dir = os.path.join(project_dir,'obj.data')
        if_exists = os.path.isfile(obj_data_dir)

        if if_exists is True:
            os.remove(obj_data_dir)

        a_class = 'classes = '+str(no_class)
        a_train = 'train = '+str(os.path.join(project_dir,'train.txt'))
        a_test = 'valid = '+str(os.path.join(project_dir,'test.txt'))
        a_names = 'names = '+str(os.path.join(project_dir,'obj.names'))
        a_backup = 'backup = '+str(os.path.join(project_dir,'backup'))

        temp_array = []
        temp_array.append(a_class)
        temp_array.append(a_train)
        temp_array.append(a_test)
        temp_array.append(a_names)
        temp_array.append(a_backup)

        #  Reference 
        # classes= 2
        # train  = /home/tericsoft/mustafa/darknet/mask/final_training.txt
        # #valid  = coco_testdev
        # valid = /home/tericsoft/mustafa/darknet/mask/final_TEST.txt
        # names = /home/tericsoft/team_alpha/personal/darknet/mask/obj.names
        # backup = /home/tericsoft/mustafa/darknet/mask/backup

        for x in temp_array:
            file_obj_names = open(obj_data_dir,'a')
            file_obj_names.writelines(x+'\n')
            file_obj_names.close()

        return obj_data_dir

def download_weights(path,backbone):
        # Below dictionary consist of back_bone whose walue is url which will download pre-trained weights
        ref_dic = {'yolov4.cfg':'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.conv.137','yolov3.cfg':'https://pjreddie.com/media/files/yolov3.weights'}
        print('Downloading pre trained weights*******',path)
        if opt.backup_weight == 'False':
            wget.download(ref_dic[backbone],project_dir)
            backbone = backbone.split('.')[0]
            weight_path = []
            sub_files = os.listdir(path)
            for x in sub_files:
                # check = x.rpartition('.')
                check = x.split('.')
                try:
                    zeta = check.index(backbone)
                    if zeta is not None:
                        full_path = os.path.join(path,x)
                        weight_path.append(full_path)
                except:
                    pass
            return weight_path[0]


def send_tele_image(data,image_path):
    try:
        updater = Updater('805281461:AAH09xnakEe8MxOBLQ7jWaiNolGxoZyxxrM')
        dp = updater.dispatcher
        token='805281461:AAH09xnakEe8MxOBLQ7jWaiNolGxoZyxxrM'
        bot = telegram.Bot(token=token)
        # if name=="unknown":
        bot.send_message(chat_id='-496362146', text=data+ str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")))
        bot.send_photo(chat_id='-496362146', photo=open(image_path,'rb'))
    except:
        print('Could Not Send TXT To Telegram')
def send_tele(data):
    try :
        updater = Updater('805281461:AAH09xnakEe8MxOBLQ7jWaiNolGxoZyxxrM', use_context=True )
        dp = updater.dispatcher
        token='805281461:AAH09xnakEe8MxOBLQ7jWaiNolGxoZyxxrM'
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id='-496362146', text=data+ str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")))
    except:
        print('SENDING ERROR IN plot')

if __name__ == "__main__":


    parser = ArgumentParser()
    parser.add_argument("--backbone", default='yolov4', help="Which yolo you want to use yolov3, yolov4")
    parser.add_argument("--project", required=True, help="Give project name")
    parser.add_argument("--batch_size", default = 16, help="Give batch size")
    parser.add_argument("--sub_batch", default =  16, help="Give batch step size")
    parser.add_argument("--epochs", default =  2000, help="Give MAX_Iterations Size here")
    parser.add_argument("--data_source", required = True, help='Provide url or google Id or path(dir)')
    parser.add_argument("--backup_weight", default = 'False', help='To use lase weights Enable it or give weight name')


    opt = parser.parse_args()

    current_dir = os.getcwd()
    bk_bone = opt.backbone
    project_name = opt.project

    project_dir = os.path.join(current_dir,project_name)
    project_is_dir = os.path.isdir(project_dir)

    if project_is_dir is False:
        back_up_dir = os.path.join(project_dir,'backup')
        os.mkdir(project_dir)
        os.mkdir(back_up_dir)

    #  If yolo_v4 then "cfg/yolov4.cfg"
    cfg_dict= {"yolov4":"yolov4.cfg", "yolov3":"yolov3.cfg"}
    selected_yolo = cfg_dict[bk_bone]
    cfg_dir = os.path.join(current_dir,'cfg',selected_yolo)

    # We need to have same name of cfg irrespective of backbone selected
    destination_cfg_dir = os.path.join(project_dir,'yolo.cfg')
    shutil.copy(cfg_dir,destination_cfg_dir)

    # Read data / Store data in project directory
    data_dir = opt.data_source
    is_dir = os.path.isdir(data_dir)
    pre_weights_path = download_weights(project_dir,selected_yolo)


    #  No download just link/ path
    if is_dir is True:

        data_folder = data_dir
        print('Data_source is a directory')
        don_train_dir, don_test_dir, don_names_dir = select_files(data_folder)

    elif is_dir is False:
        # Downloading from a URL
        data_folder = project_dir
        is_google_id_url = data_dir.find('https')
        print(' checking URL or not  ',is_google_id_url)
        if is_google_id_url != -1:
            print("Download from a URL")
            wget.download(data_dir,project_dir)
            list_sub_folder = os.listdir(project_dir)
            for x in list_sub_folder:
                check = x.find('.zip')
                if check != -1:
                    source_zip = os.path.join(project_dir,x)
                    destination_zip = project_dir

                    un_zip(source_zip,destination_zip)

        elif is_google_id_url == -1 and is_dir == False :
            # Downloading from google drive + Unzip
            print('Download from google drive')
            project_dir_zip = os.path.join(project_dir, 'custom_data.zip')

            download_file_from_google_drive(data_dir,project_dir_zip)
            sub_folder = os.listdir(project_dir)

            for x in range(len(sub_folder)):

                is_zip = sub_folder[x].find('.zip')
                if is_zip != -1:
                    zip_folder = os.path.join(project_dir,sub_folder[x])

            un_zip(zip_folder,project_dir)
     
        # Find train and test and names.txt from opt.data_source
        # give path of unzip data to select_files which has train test and names.txt
        # find downloaded folder
        print('Input data s',data_folder)
        sub_folder = os.listdir(data_folder)
        req_folder = []
        for x in sub_folder:
            full_path_x = os.path.join(data_folder,x)
            is_folder = os.path.isdir(full_path_x)
            if is_folder is True:
                print('Got the req folder',full_path_x)
                req_folder.append(full_path_x)

        don_train_dir, don_test_dir, don_names_dir = select_files(req_folder[-1])

    create_txt(don_test_dir,'test')
    create_txt(don_train_dir,'train')
    classes_nms = create_obj_names(don_names_dir)
    obj_data_directory = create_obj_data(project_dir,len(classes_nms))


    # Edit cfg file now
    edit_cfg(destination_cfg_dir,len(classes_nms))


    # Get Run command
    # ./darknet detector train mask/obj.data mask/yolo.cfg mask/yolov4.conv.137
    def use_weights(project_dir,pre_weights_path):
        dir_weight = os.path.join(project_dir,'backup',opt.backup_weight)
        is_weight_dir = os.path.isfile(dir_weight)
        if opt.backup_weight == 'True':
            # Load weights from project_dir/backup only
            weight_name = 'yolo_last.weights'
            bkup_pth = os.path.join(project_dir,'backup',weight_name)
            pre_weights_path = bkup_pth
        elif opt.backup_weight == 'False':
            print('Use downloaded weights')
        elif is_weight_dir is True:
            pre_weights_path = dir_weight
        return pre_weights_path
    pre_weights_path = use_weights(project_dir,pre_weights_path)
    
    run = './darknet detector train '+str(obj_data_directory)+' '+str(destination_cfg_dir)+' '+str(pre_weights_path)
    print('############################')
    print(run)
    print('############################')
    # exit()

    p = subprocess.Popen(run, shell=True, stdout=subprocess.PIPE)
    once_send = 'Project : ' +str(project_name) +' Backbone : '+ str(opt.backbone) +'  '
    try:
        send_tele('Training Has Been Started !!!!!')
        send_tele(once_send)
    except:
        pass

    while True:
        out = p.stdout.readline()
        all_op = out.decode("utf-8")
        iteration_line = all_op.find('avg loss,')
        end_train = all_op.find('Saving weights')

        if iteration_line != -1:
            try:
                send_tele_image(all_op,'chart.png')
                print('SEND PIC AND TEXT',all_op)
            except:
                pass
            count_iteration = all_op.split(':')[0]
            if int(count_iteration) == int(opt.epochs):
                send_tele('Training HasBeen Ended')
                break
