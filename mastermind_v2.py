import PySimpleGUI as sg
from timeit import default_timer as timer
from PIL import ImageGrab
from datetime import datetime
import random
import platform
import os
import numpy as np

sg.theme("LightBlue1")

player = "h" #(h)uman or (c)omputer
dis = sg.BUTTON_DISABLED_MEANS_IGNORE
font = ("Sans", 14)
largefont = ("Sans", 18)
boldfont = ("Source Code Pro",16,"bold")
def_col = 6 #default number of colors
def_dig = 4 #default number of digits
max_col = 8 #max number of colors
max_dig = 8 #max number of digits
max_tries = 9 #max number of guesses
colors = ["colors/red2.png","colors/blue2.png","colors/green2.png","colors/yellow2.png","colors/violet2.png","colors/marine2.png","colors/orange2.png","colors/dgreen2.png",] #available colors, "blue","green","yellow","orange","purple","light blue","brown","pink"
bg = sg.theme_background_color()
#sol = np.full((1,def_dig),-1,dtype=np.int8) #[-1]*def_digsol #init code
sol = np.array([-1 for i in range(def_dig)])
gno = 0 #guess number
count = 0 #combo counter
timetaken = 0
cc = np.full((max_tries,def_dig),-1,dtype=np.int8) #array([[-1]*def_dig for i in range(max_tries)] #initialize guesses, default
sc = np.array([random.randrange(def_col) for i in range(def_dig)]) #secret code

#https://stackoverflow.com/questions/11144513/cartesian-product-of-x-and-y-array-points-into-single-array-of-2d-points/11146645#11146645
# def cartesian_product(*arrays):
    # la = len(arrays)
    # dtype = np.result_type(*arrays)
    # arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    # for i, a in enumerate(np.ix_(*arrays)):
        # arr[...,i] = a
    # return arr.reshape(-1, la)

def cartesian_product(a,b):
	arr = np.empty([a]*b+[b], dtype=np.int8)
	for i, c in enumerate(np.ix_(*([np.arange(a)]*b))):
		arr[...,i] = c
	return arr.reshape(-1,b)

def evalcode(code,guess):
	rightg = np.count_nonzero(code==guess) #number of right guesses
	rightc = 0 #number of wrong places
	for p in set(code) & set(guess): #run over set intersection
		rightc += min(np.count_nonzero(code==p),np.count_nonzero(guess==p))
	return [rightg,rightc-rightg]

def blockeval(code,guesses):
	if any(np.count_nonzero(g[0]==code)!=g[1][0] for g in guesses): return False
	cc = np.unique(code,return_counts=True)
	cl = len(cc[0])
	if any(sum(min(cc[1][c],np.count_nonzero(g[0]==cc[0][c])) for c in range(cl))!=sum(g[1]) for g in guesses): return False
	return True

def init():
	window["human_player"].update(disabled=False)
	window["computer_player"].update(disabled=False)
	window["nodig"].update(disabled=False)
	window["nocol"].update(disabled=False)
	window["start"].update(disabled=False)
	window["button2"].update(disabled=False)
	[window["hint"+str(r)].update("") for r in range(max_tries)]
	global gno,count,timetaken
	gno = 0 
	count = 0
	timetaken = 0
	if player == "c":
		window["start"].update(text="Next guess")
		window["sol_field"].update("Your code:")
		window["button2"].update(text="Random code")
		[[window[str(r)+str(c)].update(disabled=dis,image_filename="colors/white2.png") for c in range(def_dig)] for r in range(max_tries)]
		[[window[str(r)+str(c)].update(disabled=dis,image_filename="colors/dis2.png") for c in range(def_dig,max_dig)] for r in range(max_tries)]
		[window["code"+str(c)].update(disabled=False,image_filename="colors/white2.png") for c in range(def_dig)]
		[window["code"+str(c)].update(disabled=dis,image_filename="colors/dis2.png") for c in range(def_dig,max_dig)]
		global sol
		#sol = np.full((1,def_dig),-1,dtype=np.int8) #[-1]*def_dig
		sol = np.array([-1 for i in range(def_dig)])
	if player == "h":
		window["start"].update(text="Check")
		window["sol_field"].update("Solution:")
		window["button2"].update(text="Show solution")
		[[window[str(r)+str(c)].update(disabled=False,image_filename="colors/white2.png") for c in range(def_dig)] for r in range(max_tries)]
		[[window[str(r)+str(c)].update(disabled=dis,image_filename="colors/dis2.png") for c in range(def_dig,max_dig)] for r in range(max_tries)]
		[window["code"+str(c)].update(disabled=dis,image_filename="colors/sec.png") for c in range(def_dig)]
		[window["code"+str(c)].update(disabled=dis,image_filename="colors/dis2.png") for c in range(def_dig,max_dig)]
		global cc,sc
		cc = np.full((max_tries,def_dig),-1,dtype=np.int8) #[[-1]*def_dig for i in range(max_tries)] #initialize guesses
		sc = np.array([random.randrange(def_col) for i in range(def_dig)])

menu_def = [["&Save", ["S&creenshot","E&xit"]], ["&Help", ["&Rules","&Algorithm","A&bout"]]]

frame_layout = [[sg.Text("Digits"),sg.Spin([i for i in range(4,max_dig+1)],initial_value=4,key="nodig",enable_events=True), sg.Text("   Colors"), sg.Spin([i for i in range(4,max_col+1)], initial_value=6,key="nocol",enable_events=True)]] 

layout = [
[sg.VPush()],
[sg.Menu(menu_def)],
[sg.Push(),sg.Text("Player"),sg.Radio("Human", "RAD",default=True,enable_events=True,key="human_player"), sg.Radio("Computer","RAD",enable_events=True,key="computer_player"),sg.Push()],

[sg.Push(),sg.Frame("Parameters", frame_layout,pad=(0,20)),sg.Text(key="think",text_color="yellow",size=(15,1),justification="r",font=boldfont),sg.Push()], 

[sg.Text("Guess",size=(14,1),justification="r"),sg.Text("Hint",size=(32,1),justification="r")],

[[sg.Text(str(r+1),size=(8,1),justification="r")]+[sg.Button(key=str(r)+str(c),image_filename="colors/white2.png",button_color=(bg,bg),border_width=0) for c in range(def_dig)]+[sg.Button(key=str(r)+str(c),button_color=(bg,bg),border_width=0,disabled=dis,image_filename="colors/dis2.png") for c in range(def_dig,max_dig)]+[sg.Text(key="hint"+str(r),size=(8,1))] for r in range(max_tries)], #,image_size=(31,31)

[sg.HorizontalSeparator()],

[sg.Text("Solution:",size=(8,1),key="sol_field")]+[sg.Button(key="code"+str(c),image_filename="colors/sec.png",button_color=(bg,bg),border_width=0) for c in range(def_dig)]+[sg.Button(key="code"+str(c),button_color=(bg,bg),border_width=0,image_filename="colors/dis2.png") for c in range(def_dig,max_dig)],

[sg.Text("")],
[sg.Push(),sg.Button("Check",key="start"),sg.Button("Show solution",key="button2"),sg.Button("New game",key="button3"),sg.Push()],
[sg.VPush()]]

window = sg.Window("Mastermind 2", layout,font=font,finalize=True,location=(0,0)) #,element_justification="c"

for c in range(max_dig):
	window["code"+str(c)].bind("<Button-3>","R") #right click
	for r in range(max_tries):
		window[str(r)+str(c)].bind("<Button-3>","R") #right click

while True:
	event, values = window.read() #why do we need values?
	#print(event,values) #debug

	if event in (None,"Exit",sg.WIN_CLOSED): break #is this default?

	if event == "Screenshot":
		now = datetime.now()
		stamp = now.strftime("%d-%m-%Y-%H-%M-%S")
		path = os.getcwd()+"/screenshots"
		if not os.path.exists(path): os.mkdir(path)
		filename = sg.popup_get_file("Choose file (PNG, JPG, GIF) to save to", save_as=True,default_path=path+"/game"+stamp+".jpg")
		if filename == None: continue
		cl = window.CurrentLocation()
		si = window.size
		box = (cl[0],cl[1],cl[0]+si[0],cl[1]+si[1])
		grab = ImageGrab.grab(bbox=box)
		grab.save(filename)

	if event == "About":
		sg.popup("Created with:\n   – Python "+str(platform.python_version())+"\n   – PysimpleGUI "+str(sg.version)[0:6]+"\n   – LaTeX + PGF/TikZ 3.1.9a\n   – MtPaint 3.51\n\nby Benjamin Sambale",title="About",font=largefont,background_color="orange",text_color="black")

	if event == "Rules":
		sg.popup_scrolled("As a 𝗵𝘂𝗺𝗮𝗻 𝗽𝗹𝗮𝘆𝗲𝗿 your task is to determine a secret color code randomly generated by the computer. The length of the code is given by the digit counter and defaults to 4. It can be increased up to 8. Similarly, you may change the number of colors from 4 to 8 (default is 6). The higher both numbers are, the harder your task gets. You cannot change the parameters of an ongoing game (click 𝘕𝘦𝘸 𝘨𝘢𝘮𝘦 instead). Note that the computer may choose a color multiple times or not even once.\nYou start entering your guesses from top to bottom by clicking on the white circles. For convenience, a click on the right mouse button reverses a left button click. Once a row has been set completely, press 𝘊𝘩𝘦𝘤𝘬 to obtain hints as shown on the right. The first hint tells you the number of correctly placed colored circles, but not where they are. The second hint counts the incorrect circles, which can be swapped to their correct positions. The sum of the hints cannot exceed the total number of digits. To get a better understanding, you may try the computer player mode first (described below). Once all circles are correct, you win. If you cannot make this in 9 tries, you loose.\n\nIn the 𝗰𝗼𝗺𝗽𝘂𝘁𝗲𝗿 𝗽𝗹𝗮𝘆𝗲𝗿 𝗺𝗼𝗱𝗲 you first need to enter a (secret) code at the button. If lazy, take a random code generated by pressing that button. Now let the computer guess by pressing 𝘕𝘦𝘹𝘵 𝘨𝘶𝘦𝘴𝘴. It will also take care of displaying the hint. Since this requires the knowledge of the secret code, we must trust that the computer will not abuse this knowledge for its guesswork. If played with many digits and colors, guessing can take a few minutes. If you manage to let the computer loose, take a screenshot and enjoy.",title="Rules",background_color="orange",font=("Sans", 14),text_color="black",size=(40,20))

	if event == "Algorithm":
		sg.popup_scrolled("Each code with 𝑑 digits and 𝑐 colors represents the 𝑐-adic expansion of an integer in the list 𝐿 = [0..𝑐ᵈ–1]. The computer generates its guesses as follows: For 𝑖 = 𝑐ᵈ–1 choose a random integer 𝑟 in [0..𝑖]. If the 𝑐-adic expansion of 𝐿[𝑟] is consistent with all previous hints, let 𝐿[𝑟] be the next guess. If 𝐿[𝑟] is inconsistent with the hints or if the guess was incorrect, swap 𝐿[𝑟] with 𝐿[𝑖] and decrease 𝑖. Now repeat. This procedure generates feasible codes in a uniformly random order without picking the same code twice (Fisher-Yates algorithm). The randomness lowers the average number of required guesses compared to a fixed (say lexicographical) order. At the same time, it makes the computer game more entertaining. Note that the python function \"shuffle\" does not always yield a uniformly random permutation of 𝐿 due to the enormous number of all permutations (𝑐ᵈ!).\n\nDonald Knuth has shown that the standard game with (𝑑,𝑐)=(4,6) can always be solved in at most 5 tries (using some inconsistent guesses). This, however, does not yield the smallest average number of guesses. For more information, visit Wikipedia.",title="Algorithm",background_color="orange",font=("Sans", 14),text_color="black",size=(40,20))

	if player == "h" and event == "computer_player":
		player = "c"
		init()
		
	if player == "c" and event == "human_player":
		player = "h"
		init()

	if event == "nodig":
		def_dig = window.Element("nodig").Get()
		init()
		
	if event == "nocol":
		def_col = window.Element("nocol").Get()
		init()

	if player == "c" and event[:4] == "code": 
		if len(event) == 5:
			sol[int(event[4])] = (sol[int(event[4])]+1) % def_col #increase solution with left click
			window[event].update(image_filename=colors[sol[int(event[4])]])
		if len(event) == 6:
			if sol[int(event[4])] == -1: #start position
				sol[int(event[4])] = def_col-1
			else:
				sol[int(event[4])] = (sol[int(event[4])]-1) % def_col #decrease solution with right click
			window[event[:5]].update(image_filename=colors[sol[int(event[4])]])
		window["nodig"].update(disabled=True)
		window["nocol"].update(disabled=True)

	if player == "c" and event == "start":
		if gno == max_tries or -1 in sol: continue
		if count == 0: #initialize
			sh = cartesian_product(def_col,def_dig)
			cd = def_col**def_dig #number of combinations
			[window["code"+str(c)].update(disabled=dis) for c in range(def_dig)]
			window["button2"].update(disabled=True)
			window["human_player"].update(disabled=True)
			window["computer_player"].update(disabled=True)
			gu = [[np.empty(def_dig,dtype=np.int8),np.empty(2,dtype=np.int8)] for i in range(max_tries)] #computer guesses+hints
		window["think"].update("…thinking…")
		start = timer()
		window.refresh()
		while True:
			r = random.randrange(0,cd-count)
			count += 1
			if blockeval(sh[r],gu[:gno]): 
				gu[gno][0] = np.array(sh[r])
				gu[gno][1] = evalcode(sol,gu[gno][0])
				sh[r] = sh[cd-count]
				break
			sh[r] = sh[cd-count] 
		end = timer()
		timetaken += end-start
		window["think"].update("")
		[window[str(gno)+str(d)].update(image_filename=colors[gu[gno][0][d]]) for d in range(def_dig)]
		if gu[gno][1][0] < def_dig:
			window["hint"+str(gno)].update(" "+str(gu[gno][1][0])+"  "+str(gu[gno][1][1]))
			window["hint"+str(gno)].set_tooltip(str(gu[gno][1][0])+" correctly placed circle(s) and\n"+str(gu[gno][1][1])+" more circle(s) in the correct color but wrong position")
		if gu[gno][1][0] == def_dig:
			window["hint"+str(gno)].update("  ✓")
			window["hint"+str(gno)].set_tooltip("all circles correct!")
			sg.popup("Solved in "+str(gno+1)+" tries and "+"%.2f" % timetaken+" seconds!",title="I won!",font=largefont,background_color="orange",text_color="black",any_key_closes=True)
			window["start"].update(disabled=True)
		if gno == max_tries-1 and gu[gno][1][0] < def_dig: #
			sg.popup("Not solved in "+str(max_tries)+" tries :-(",title="I lost!",font=largefont,background_color="grey",text_color="black",any_key_closes=True)
			window["start"].update(disabled=True)
		gno += 1

	if player == "h" and isinstance(event,str) and len(event) in [2,3]: #one of the grid buttons is clicked
		window["human_player"].update(disabled=True)
		window["computer_player"].update(disabled=True)
		if len(event) == 2: #left mouse button
			cc[int(event[0]),int(event[1])] = (cc[int(event[0]),int(event[1])]+1) % def_col 
			window[event].update(image_filename=colors[cc[int(event[0])][int(event[1])]])
		if len(event) == 3: #right mouse button
			if cc[int(event[0]),int(event[1])] == -1: #start position
				cc[int(event[0]),int(event[1])] = def_col-1
			else:
				cc[int(event[0]),int(event[1])] = (cc[int(event[0]),int(event[1])]-1) % def_col 
			window[event[:2]].update(image_filename=colors[cc[int(event[0]),int(event[1])]])
		window["nodig"].update(disabled=True)
		window["nocol"].update(disabled=True)
	
	if player == "h" and event == "start":
		if gno == max_tries or -1 in cc[gno]: continue
		if gno == 0: start = timer()
		h = evalcode(cc[gno],sc)
		if h[0] < def_dig:
			window["hint"+str(gno)].update(" "+str(h[0])+"  "+str(h[1]))
			window["hint"+str(gno)].set_tooltip(str(h[0])+" correctly placed circle(s) and\n"+str(h[1])+" more circle(s) in the correct color but wrong position")
		if h[0] == def_dig:
			timetaken = timer()-start
			window["hint"+str(gno)].update("  ✓")
			window["hint"+str(gno)].set_tooltip("all circles correct!")
			[window["code"+str(c)].update(image_filename=colors[sc[c]]) for c in range(def_dig)]
			[[window[str(c)+str(r)].update(disabled=dis) for c in range(max_tries)] for r in range(def_dig)]
			sg.popup("Solved in "+str(gno+1)+" tries and "+"%.2f" % timetaken+" seconds!",title="You won!",font=largefont,background_color="orange",text_color="black",any_key_closes=True)
			window["start"].update(disabled=True)
			window["button2"].update(disabled=True)
		if gno == max_tries-1 and h[0] < def_dig:
			[window["code"+str(c)].update(image_filename=colors[sc[c]]) for c in range(def_dig)]
			[[window[str(c)+str(r)].update(disabled=dis) for c in range(max_tries)] for r in range(def_dig)]
			sg.popup("Not solved in "+str(max_tries)+" tries :-(",title="You lost!",font=largefont,background_color="grey",text_color="black",any_key_closes=True)
			window["start"].update(disabled=True)
			window["button2"].update(disabled=True)
		[window[str(gno)+str(c)].update(disabled=dis) for c in range(def_dig)]
		gno += 1
	
	if player == "c" and event == "button2":
		sol = np.array([random.randrange(def_col) for c in range(def_dig)])
		[window["code"+str(c)].update(image_filename=colors[sol[c]]) for c in range(def_dig)]
		window["nodig"].update(disabled=True)
		window["nocol"].update(disabled=True)
		window["human_player"].update(disabled=True)
		window["computer_player"].update(disabled=True)
		
	if player == "h" and event == "button2":
		[window["code"+str(c)].update(image_filename=colors[sc[c]]) for c in range(def_dig)]
		window["button2"].update(disabled=True)
		window["start"].update(disabled=True)
		[[window[str(c)+str(r)].update(disabled=dis) for c in range(max_tries)] for r in range(def_dig)]

	if event == "button3":
		init()
		
window.close()
