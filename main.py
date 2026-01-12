from panda3d.core import loadPrcFileData
loadPrcFileData("", "load-display pandagl")
loadPrcFileData("", "window-type onscreen")
from pytubefix import YouTube
from pytubefix.exceptions import VideoUnavailable, RegexMatchError
from ursina import *
import threading
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pathlib import *
import os
import re



def safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', '', name)



link = ""

app = Ursina(development_mode = False , title="S-Downloader" , icon = "textures/Logo.ico" , fullscreen=False, borderless=False)
window.exit_button.visible = False

bg = Entity(parent=scene, model="quad" , texture="textures/Abstract-White-Background.mp4" ,scale=(20,10) , x = 0 , y =0 , z= 1)

loading = Entity(parent=scene, model="quad" , texture="textures/loading-circle.mp4" ,scale=(1 , 1) ,  position=(0 , 1.5 , 0))
loading.enabled = False



video_name = Text("" ,  position = (-0.2 , 0.36 , 0) , color = color.black , scale=(2,2) ,  x=0, origin=(0, 0))
video_name.enabled = False

resolutionmenu = Entity(parent=scene ,texture="white_cube" , model="quad", scale=(3 * 2 , 3.5 * 2) , color=color.dark_gray , position=(0 , -1.2 , 0))
resolutionmenu.enabled = False

resolutionmenu.alpha = (85)/100


resolutionButtons = []

def show_resolution_menu(link : str ,resolutions : list):
    inp.enabled = False
    b1.enabled = False
    b2.enabled = False
    resolutionmenu.enabled = True

    for i in range (len(resolutions)):

        resolutionButtons.append(Button(text=resolutions[i].resolution,
               color=color.white,
               parent=scene, text_size=0.5,
               scale=(3, 0.5),
               z=-1,
               y=-((i * 0.7)) + 1.6,
               text_color=color.black,
               tooltip=Tooltip(resolutions[i].resolution),
               on_click=Func(downloadv_thread, str(link) , int(resolutions[i].itag))))


        #int(resolutions[i].itag)

def hide_resolution_menu():
    resolutionmenu.enabled = False
    for i in resolutionButtons:
        destroy(i)



# title = Text("S-Downloader" , position = (-0.2 , 0.44 , 0) , color = color.black , scale=(2,2) ,  x=0, origin=(0, 0))


download_status = Text("Downloading!" , position = (-0.2 , 0 , 0) , color = color.black , scale=(2,2) , x=0, origin=(0, 0))
download_status.enabled = False




inp = InputField(active= True , scale=(1 , 0.07 , 1) , position=(0 , 0 , -1))




# load = Animation("content/ezgif-frame" , fps = 20 , loop=True , autoplay=True , position=(0 , 1 , -2) , scale=(3 , 3 , 3))

# a = Animator(
#     animations={
#         "idle" : Entity(model="quad" , color = color.hex("#170c2a") , position=(0 , 2 , -2)),
#         "loading" : load
#     }
# )

# a.state = "idle"


def submit(link , type):
    t1 = threading.Thread(target=Downloada, args=(link , type))
    t1.start()
    loading.enabled = True
    hide_resolution_menu()
    download_status.enabled = True





b1 = Button(text= "download video" , scale=0.1 , scale_x= (0.5) ,x = 0.3 , y= -0.2)
b2 = Button(text= "download audio" , scale=0.1 , scale_x= (0.5) ,x = -0.3 ,y= -0.2)
b1.enabled = False
b2.enabled = False

def is_valid_youtube_link(link: str) -> bool:
    try:
        yt = YouTube(link)
        # Force fetch to confirm the video exists
        _ = yt.title

        return True
    except (VideoUnavailable, RegexMatchError, Exception):
        return False


def inpenter():
    link = inp.text

    if inp.active and link != "":
        print("Input Confirmed:", link)
        if is_valid_youtube_link(link):
            lv = []
            yt = YouTube(link)
            resolutionsvid = yt.streams.order_by('resolution').filter(mime_type='video/mp4')
            for j in resolutionsvid:
                if ("av01" in j.video_codec) or (j.is_progressive == True):
                    lv.append(j)
            b1.enabled = True
            b1.on_click = Func(show_resolution_menu , link ,lv)
            b2.on_click = Func(submit , link ,"audio")
            b2.enabled = True
            inp.text = ""
            inp.enabled = False
            video_name.text = "Video:\n" + yt.title
            video_name.enabled = True


inp.on_submit = inpenter





def combine_audio(vidname,
                  audname,
                  outname,
                  fps):
    video = VideoFileClip(vidname)
    audio = AudioFileClip(audname)
    final_clip = video.set_audio(audio)
    final_clip.write_videofile(outname,fps=fps)



def open_menu():
    b1.collision = False


def Downloada(link , type):
    try:
        youtubeObject = YouTube(link)
    except (RegexMatchError, VideoUnavailable) as e:
        print("Invalid YouTube link:", link)
        loading.enabled = False
        return

    #split ----------

    l = []
    resolutions = youtubeObject.streams.order_by('resolution').filter(mime_type='video/mp4')
    audios = youtubeObject.streams.order_by('abr').filter(mime_type='audio/mp4')

    for j in resolutions:
        if "av01" in j.video_codec:
            l.append(j)


    highest_res = l[len(l) - 1]
    highaudio = audios[len(audios) - 1]

    #combine_audio( , , , highest_res.fps)

    #split--------------


    #split -------------
    youtubeObjecta = youtubeObject.streams.get_by_itag(highaudio.itag)
    print("started downloading")
    # a.state = "loading"
    loading.enabled = True


    if type == "audio":
        youtubeObjecta.download('downloads')
    else:
        print("error with type identification")
    print("Download is completed successfully")
    # a.state = "idle"
    loading.enabled = False
    download_status.enabled = False
    inp.enabled = True
    video_name.text = "Download Successful!"

def downloadv_thread(link : str , itag : int):
    t = threading.Thread(target=Downloadv , args=(link , itag))
    t.start()
    loading.enabled = True
    hide_resolution_menu()
    download_status.enabled = True






def Downloadv(link : str , itag : int):
    youtubeObject = YouTube(link)


    #split ----------

    audios = youtubeObject.streams.order_by('abr').filter(mime_type='audio/mp4')




    highaudio = audios[len(audios) - 1]

    #combine_audio( , , , highest_res.fps)

    #split--------------


    #split -------------
    youtubeObjectv = youtubeObject.streams.get_by_itag(itag)
    youtubeObjecta = youtubeObject.streams.get_by_itag(highaudio.itag)
    print("started downloading")
    # a.state = "loading"



    if youtubeObjectv.is_progressive == True:
        youtubeObjectv.download('downloads')

    else:
        video_path = youtubeObjectv.download('junk')
        audio_path = youtubeObjecta.download('junk')
        folder_path = Path("downloads")

        try:
            folder_path.mkdir()
            print(f"Folder '{folder_path}' created.")
        except FileExistsError:
            print(f"Folder '{folder_path}' already exists.")

        safe_title = safe_filename(youtubeObject.title)
        output_path = f"downloads/{safe_title}.mp4"

        combine_audio(
            video_path,
            audio_path,
            output_path,
            fps=youtubeObjectv.fps
        )



    print("Download is completed successfully")
    # a.state = "idle"
    os.remove(video_path)
    os.remove(audio_path)
    loading.enabled = False
    download_status.enabled = False
    inp.enabled = True
    video_name.text = "Download Successful!"





def test(string):
    print(string)
def input(key):
    if key == 'enter':
        inpenter()

app.run()
