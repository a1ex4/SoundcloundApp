from tkinter import *
from tkinter import font
from tkinter import ttk
from functools import partial
from soundcloud import Client
import urllib
from os import path, makedirs, environ, getcwd
from time import strftime
import threading
import subprocess
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1
from getpass import getuser



# *** Variables ***
environ["REQUESTS_CA_BUNDLE"] = path.join(getcwd(), "cacert.pem")
soundcloud = None
memory = 'Can do!'
search_default = 'Nice'
user = False 
to_dl = []
wuser=getuser()
format = '.mp3'
date = str(strftime("%d")) +' '+ str(strftime("%b"))



# *** Functions ***
def click_entry(event):
    search.delete(0, END)
    search.configure(style ='searchA.TEntry')

  

def tracklist (tracks):
    go = ttk.Button(mainFrame, text ="Go !", command = soundcloud.download)
    go.pack(side =RIGHT, anchor = S, padx= (15,50), pady=(0,10))
    
    opendir = ttk.Button(mainFrame, text ="Open dir.", command=opendir_func)
    opendir.pack(side =RIGHT, anchor = S, pady=(0,10))
    
    global progressbar
    int_var = IntVar()
    progressbar = ttk.Progressbar(mainFrame,orient="horizontal",length=600, value = 100, mode="determinate", maximum = 100)
    progressbar["variable"] = int_var
    progressbar.pack(side =RIGHT, anchor = S, pady=(0,11), padx=(5,20))
    
    global info
    info = ttk.Label(mainFrame)
    info.pack(side=RIGHT, pady=(0,5))
    
    canvas=Canvas(mainLayout)
    newframe=Frame(canvas)
    myscrollbar=Scrollbar(mainLayout,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)
    
    myscrollbar.pack(side="right",fill="y",)
    canvas.create_window((0,0),window=newframe,anchor=NW,)
    canvas.pack(side=RIGHT, fill =BOTH, expand = 1)
    
    newframe.bind("<Configure>",lambda event:canvas.configure(scrollregion=canvas.bbox(ALL)) )
    i=0
    global container
    container={}
    for track in tracks: 
        title = str(i) + "_title_label"
        container[title] = MyLabel(newframe, text=track.title, myborderwidth=1, mybordercolor='#d5d5d5', myborderplace='centerr',width = 70, height = 3, background ='white', anchor = W, padx = 15, fg ='#3c3c3c')
        container[title].grid(row=i)
        
        artist = str(i) + "_artist_label"
        container[artist] = MyLabel(newframe, text=track.user["username"], myborderwidth=1, mybordercolor='#d5d5d5', myborderplace='center',width = 20, height = 3, background ='white', anchor = W, padx=15,fg ='#3c3c3c',)
        container[artist].grid(row = i, column = 1)
        
        dl = str(i) +"_dl_label"
        image_cross = PhotoImage(file='cross.png')
        container[dl]= Label(newframe, text= "not_ok", image = image_cross,width = 46, height = 46)
        container[dl].image= image_cross
        container[dl].grid(row = i, column = 2)
        
        
        i+=1
        
    for j in range(i):
        dlj= str(j) +"_dl_label"
        titlej= str(j) +"_title_label"
        artistj= str(j) +"_artist_label"
        def image_lambda(x, j):
            return lambda event:image(event,x,j)
        
        def label_lambda(x):

            return lambda event:main2(x)

        container[dlj].bind("<Button-1>", image_lambda(dlj,j))
        container[titlej].label.bind("<Double-Button-1>", label_lambda(titlej)) 
        container[artistj].label.bind("<Double-Button-1>", label_lambda(artistj)) 

    def image(event, ref,j):
        if container[ref].cget("text") == "not_ok":
            to_dl.append(j)
            image_ok = PhotoImage(file ='ok.png')
            container[ref].configure(text ="ok",image = image_ok)
            container[ref].image= image_ok
        elif container[ref].cget("text") == "ok":
            to_dl.remove(j)
            image_cross = PhotoImage(file ='cross.png')
            container[ref].configure(text ="not_ok",image = image_cross)
            container[ref].image= image_cross
        
        
    def main2(ref):
        newtext_wd = Tk()
        newtext_wd.title("Rename song")
        text = container[ref].label.cget("text")
        rename=ttk.Label(newtext_wd,text="Rename the title/artist of the song :")
        rename.pack(side=TOP, anchor=W, padx=20, pady=5)
        entry_newtext = ttk.Entry(newtext_wd, width=len(text) + 2, justify = CENTER)
        entry_newtext.insert(0, text)
        entry_newtext.pack(padx=20)
        
        def ok(e):
            newtext = entry_newtext.get()
            container[ref].label.configure(text=newtext)
            newtext_wd.destroy()

        entry_newtext.bind("<Return>",ok)
        okbt = ttk.Button(newtext_wd,text="Ok", command=ok)
        okbt.pack(pady=5)
        
        
    
        newtext_wd.mainloop()
    
    
    def label_text(event,ref, text):
        container[ref].label.configure(text=text)
            

        
    

def opendir_func():
    subprocess.check_call([r'explorer', mypath])



class MyLabel(Frame):
    '''inherit from Frame to make a label with customized border'''
    def __init__(self, parent, myborderwidth=60, mybordercolor=None,
                 myborderplace='center', *args, **kwargs):
        Frame.__init__(self, parent, bg=mybordercolor)
        self.propagate(False) # prevent frame from auto-fitting to contents
        self.label = Label(self, *args, **kwargs) # make the label

        # pack label inside frame according to which side the border
        # should be on. If it's not 'left' or 'right', center the label
        # and multiply the border width by 2 to compensate
        self.label.pack(side=BOTTOM)
        myborderwidth2 = myborderwidth * 2

        # set width and height of frame according to the req width
        # and height of the label
        if myborderplace =='centerr':
            self.config(width=self.label.winfo_reqwidth() + myborderwidth2)
        else :
            self.config(width=self.label.winfo_reqwidth() + myborderwidth)
        self.config(height=self.label.winfo_reqheight()+ myborderwidth)



def hover(widget,event):
    widget.configure(style ='btnClick.TLabel')
    

def search_text_after(event):
    search.configure(style='searchA.TEntry')
    
def search_text_before(event):
    search.configure(style='searchB.TEntry')

def label_hover(widget, event):
    widget.configure(background = '#111', foreground = 'white')
    
def label_quit(widget,event):
    widget.configure(style='btn.TLabel')

def status_text(newtext):
    memory = statusBar.cget("text")
    statusBar.configure(text = newtext)
    
def combine_enter(widget, event, newtext):
    hover(widget, event)
    statusBar.configure(text = newtext)
    
def combine_leave(widget,event, newtext):
    label_quit(widget, event)
    statusBar.configure(text = newtext)
    
def main_favorites(event,limit):
    global mypath
    mypath= "C:\\Users\\" + wuser+"\\Music\\Soundcloud\\Likes "+ date
    if not path.exists(mypath): makedirs(mypath)
    if soundcloud is not None:
        global tracks
        tracks = soundcloud.favorites(limit)
        tracklist(tracks)
    else:
        main(event)

def main_user(event):
    url = search.get()
    global tracks
    tracks = soundcloud.user(url)
    tracklist(tracks)

def main(event):
    global login
    login = Tk()
    login.title("Login")
    app = LoginFrame(login)
    login.mainloop()
    


    

class SoundcloudObject:

    def __init__(self, user, pw):
        self.auth(user,pw)
        """ Authentification """
        client = Client(
        
        client_id = '00d3fbad6f8ab649c131d0e558f8387d',
        client_secret = '8b7d292013c5f4ddbbacccfee6059a54',
        username = str(user),
        password = str(pw)
        )

    def auth(self, user, pw):
        self.client = Client(
        
        client_id = '00d3fbad6f8ab649c131d0e558f8387d',
        client_secret = '8b7d292013c5f4ddbbacccfee6059a54',
        username = str(user),
        password = str(pw)
        )
        
    def favorites(self, limit):
        tracks = self.client.get('/me/favorites', limit=limit)
        return tracks
        
    def username(self):
        return self.client.get('/me').username
    
    def user(self, url):
        user = self.client.get('/resolve', url=url)
        artist_username = str(user.username)
        global mypath
        mypath= "C:\\Users\\" + wuser+"\\Music\\"+ artist_username
        if not path.exists(mypath): makedirs(mypath)
        id= str(user.id)
        request = '/users/' +id+'/tracks'
        tracks =  self.client.get(request)
        return tracks
        
    def download(self):
            thread = threading.Thread(target=self.dl_thread)
            thread.start()
            
    
    def dl_thread(self):
        for track in tracks:
            no=tracks.index(track)
            if not no in to_dl:
                continue
            global title
            title_c = str(no)+"_title_label"
            title = container[title_c].label.cget("text")
            info.configure(text = 'Downloading  '+ title)
            global artist
            artist_c=str(no)+"_artist_label"
            artist = container[artist_c].label.cget("text")
            cover_url = track.artwork_url   #low-res
            global cover
            cover = cover_url.replace("large","t500x500")   #high-res
            stream_url = self.client.get(track.stream_url, allow_redirects=False)
            global url
            url = stream_url.location.replace('https', 'http')
            filename= title +format
            global fullfilename
            fullfilename = path.join(mypath, filename)
#             while progressbar["value"] < 99 :
#                 pass
            urllib.request.urlretrieve(url, fullfilename, reporthook=self.progress)
            self.add_tags(title, artist, cover, fullfilename)
            info.configure(text = 'Done.')
            progressbar["value"] = 0

            
    def progress(self,count, blocksize, totalsize):
            """ count : number of blocks downloaded ; blockSize : size of a single block (8192) ; total size of the file. urlretrieve update the content constantly"""
        
            bytesdownloaded = blocksize*count
            mbdownloaded = bytesdownloaded/1024/1024
            mbsize = float(blocksize)/float(totalsize)
            totalsize = totalsize/1024/1024
            percent = mbsize*100
            progressbar.step(percent)
    
    def add_tags(self,title, artist, cover, fullfilename):
        file = MP3(fullfilename, ID3=ID3)
    
        try:
            file.add_tags()
        except error:
            pass
        #Cover
        file.tags.add(
            APIC(
                encoding=3, # 3 is for utf-8
                mime='image/png', # image/jpeg or image/png
                type=3, # 3 is for the cover image
                desc=u'Cover',
                data=urllib.request.urlopen(cover).read()   
            )
        )
        #Title
        file.tags.add(
            TIT2(encoding=3, text= title)
            )
        #Artist
        file.tags.add(
            TPE1(encoding=3, text= artist)
            )
        
        file.save()
        
        
#             total = totalSize//blockSize    #    number of blocks it will take to download the entire file
#             percent = int(100*count//total)     #   number of blocks for 1% of the file
#             progressbar["value"] = percent
#             pbar.update(percent)    #update the progress bar by 1% if reached
        
        

        



# Main window
root = Tk()
root.iconbitmap(default = r"C:\Users\Alexandre\Desktop\unnamed.ico")
root.title("Soundcloud App")
root.configure(bg='white')
root.geometry('1200x600')




# *** Status Bar ***


statusBar = Label(root, text = memory, bd = 1, relief = SUNKEN, anchor = W)
# print (statusBar.get(text))
statusBar.pack(side=BOTTOM,fill = X)

# *** Top Border ***


font_label = font.Font(family='Interstate', size=14)
font_tracks = font.Font(family='Interstate', size=10)
font_label_login = font.Font(family='Interstate', size=15)
font_label_search = font.Font(family='Interstate', size=9)

border_style= ttk.Style()
border_style.configure('My.TFrame', background = '#333')
topFrame= ttk.Frame(root, style='My.TFrame')
topFrame.pack(side = TOP, fill=X)

# *** Main Layout ***

mainFrame = ttk.Frame(root)
mainFrame.pack(fill = BOTH, expand = 1)



mainLayout=Frame(mainFrame)
mainLayout.pack( fill =BOTH, expand =1, padx=30, pady=30)


button_style = ttk.Style()
button_style.configure('btn.TLabel', background = '#333', padding = 10, font = font_label, foreground ='#ccc')
button_style.configure('btnClick.TLabel', background = '#111', padding = 10, font = font_label, foreground ='white')

search_style_before = ttk.Style()
search_style_before.configure('searchB.TEntry', foreground='#ccc')
search_style_before.configure('searchA.TEntry')



login_label = ttk.Label(topFrame, text = "Login", style = 'btn.TLabel', foreground ='#f50', font = font_label_login)
login_label.bind("<Button-1>", main)
login_label.bind("<Enter>", lambda event,  var = 'Click to login': status_text(var) )
login_label.bind("<Leave>", lambda event,  var = memory: status_text(var))
login_label.pack(side=LEFT) 

def change_search(event,newtext):
    search.delete(0, END)
    search.insert(0,newtext)
    search.configure(style ='searchB.TEntry')
    
search = ttk.Entry(topFrame, width = 60, font = font_label_search, style='searchB.TEntry')
search.bind("<Button-1>", lambda event : click_entry(event))
search.bind("<Return>", lambda event: main_user(event))
search.pack(side=LEFT, padx=(300,20))

# playlist_label = ttk.Label(topFrame, text = "Playlist", style = 'btn.TLabel')
# playlist_label.bind("<Button-1>",lambda event, newtext = 'https://soundcloud.com/ddmrecordings/sets/imagined-herbal-flows-floating': change_search(event,newtext))
# playlist_label.bind("<Enter>", lambda event,  var ='Playlist From Url': combine_enter(playlist_label, event, var) )
# playlist_label.bind("<Leave>", lambda event,  var = memory: combine_leave(playlist_label, event, var))
# playlist_label.pack(side=RIGHT)

user_label = ttk.Label(topFrame, text = "User", style = 'btn.TLabel')
user_label.bind("<Button-1>", lambda event , newtext = 'https://soundcloud.com/porter-robinson' : change_search(event, newtext))
user_label.bind("<Enter>", lambda event,  var ='Tracks Posted By The User': combine_enter(user_label, event, var) )
user_label.bind("<Leave>", lambda event,  var = memory: combine_leave(user_label, event, var))
user_label.pack(side=RIGHT)

# stream_label = ttk.Label(topFrame, text = "Stream", style = 'btn.TLabel')
# stream_label.bind("<Enter>", lambda event,  var ='Show Stream': combine_enter(stream_label, event, var) )
# stream_label.bind("<Leave>", lambda event,  var = memory: combine_leave(stream_label, event, var))
# stream_label.pack(side=RIGHT)  

likes_label = ttk.Label(topFrame, text = "Likes", style = 'btn.TLabel')
likes_label.bind("<Button-1>",lambda event , var = 40: main_favorites(event,var))
likes_label.bind("<Enter>", lambda event,  var ='Recently Favorited Songs': combine_enter(likes_label, event, var) )
likes_label.bind("<Leave>", lambda event,  var = memory: combine_leave(likes_label, event, var))
likes_label.pack(side=RIGHT) 





loupe = PhotoImage(file="loupe.png")
loupe_label =  ttk.Label(topFrame, image = loupe, background='#333')
loupe_label.pack(side=LEFT)




#*** Login window ***


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.label_1 = ttk.Label(self, text="Email: ")
        self.label_2 = ttk.Label(self, text="Password: ")

        self.entry_1 = ttk.Entry(self)
        self.entry_2 = ttk.Entry(self, show="*")
 
        self.label_1.grid(row=0, sticky=E, pady=5, padx=(5,5))
        self.label_2.grid(row=1, sticky=E, pady=5,padx=(5,5))
        self.entry_1.grid(row=0, column=1, padx=(0,10))
        self.entry_2.grid(row=1, column=1, padx=(0,10))
       
        self.logbtn = ttk.Button(self, text="Login", command = self.login)
        self.logbtn.grid(columnspan=2, pady=(4,5))

        self.pack()

    def login(self):
        username = self.entry_1.get()
        password = self.entry_2.get()
        global soundcloud
        soundcloud = SoundcloudObject(username,password)
        nick = soundcloud.username()
        login_label.configure(text = nick)
        login_label.bind("<Enter>", lambda event,  var ='Hello '+ nick + ' ! <3': status_text(var) )
        login.destroy()
    



root.mainloop()
