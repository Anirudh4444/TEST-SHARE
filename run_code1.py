import pyttsx3
import os
import pathlib
from file_read_backwards import FileReadBackwards
from subprocess import call
import subprocess
import tkinter as tk
from tkinter import filedialog

engine = pyttsx3.init('sapi5')
print(engine)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def choose_file():
    print("Bot: "+"Browse file to run")
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames()
    #print(files,type(files),len(files))
    if not files:
        speak("Sorry , you haven't chosen any valid file ,Aborting ,run code "
              "command")
        print("You haven't chosen any valid file ,aborting run code "
              "command")
    if len(files) > 0:
        for file in files:
            run_code(os.path.abspath(file))

def run_code(filename):
    # print(filename)
    # print(os.path.basename(filename).split(".")[1])
    if not os.path.basename(filename).split(".")[1] == "py":
        speak("Sorry , you haven't chosen any valid file ,Aborting ,run code "
              "command")
        print("Bot:"+"You haven't chosen any valid file ,aborting run code "
              "command")
    # print(os.path.basename(filename))
    logfilename=os.path.basename(filename).split(".")[0]+"_log.txt"
    #print(logfilename)
    try:
        with open(logfilename, 'w') as f:
            speak("Running your code...")
            print("Bot:"+"Running your code...")
            # print(filename)

            call(['python', filename],timeout=5,stdout=f,stderr=f)

    except Exception as e:
        speak("Code took too long to run")
        print("Bot:"+"Code took too long to run")
        strfile = open(logfilename, 'r').read()
        filesize = os.path.getsize(logfilename)
        #print(filesize)
        if (filesize == 0) or ((strfile.find('Traceback') == -1) and ((
                strfile.find('File') == -1 and
                                                   (strfile.find('line') ==
                                                    -1 )))):
                speak("The code has no compile time errors,if code is "
                      "interactive please run with inputs on shell or IDE")
                print("Bot:"+"The code has no compile time errors,if code is "
                            "interactive please run with inputs on shell or IDE")
                return False


    strfile = open(logfilename, 'r').read()
    #print("file",strfile)
    if (strfile.find('Traceback') == -1) and ((strfile.find('File') == -1 and
                                              (strfile.find('line') == -1 ))):
        filesize = os.path.getsize(logfilename)
        # print(filesize)
        # print("f",strfile,type(strfile))
        if filesize == 0:
            speak("The code ran without errors or exceptions ")
            return True
        if not (strfile and strfile.strip()):
            speak("The code ran without errors or exceptions ")
            return True
        else:
            speak("The code ran without errors or exceptions and "
            "your "
            "output is")
            speak(strfile)
            return True
    else :
        with open(logfilename, 'r') as f:
            lastline = f.read().splitlines()[-1]
            speak("The error or exception in your code is"+lastline.split(":")[0])
            print("Bot: "+"The error or exception in your code "
                          "is "+lastline.split(":")[0])
            speak("And the cause of your error is"+lastline.split(":",1)[1])
            print("Bot: "+"And the cause of your error is "+lastline.split(
                ":",1)[1])
            with FileReadBackwards(logfilename) as frb:
                flag=False
                for l in frb:
                    if not flag:
                        if ('line' in l) and ('File' in l):
                            trace=l.split(" ")
                            #print(trace)
                            line_number=trace[trace.index('line')+1].replace('\"','')
                            if 'in' in trace:
                                module=\
                                trace[trace.index( 'in')+1].replace( '\"','')
                            else :
                                module=False
                            path_name=trace[trace.index('File')+1].replace('\"','')
                            # print("trace",trace,"i",trace[trace.index(
                            #     'File')+1].replace('\"',''))
                            directory=path_name.rsplit('\\',1)[0]
                            file=path_name.rsplit('\\',1)[-1]
                            #print(filename.rsplit('\\',1)[0])
                            # print(path_name,directory,"file",file,"pdf")
                            #print("check",directory,filename.rsplit('\\',1)[0])
                            if directory == filename.rsplit('\\',1)[0]:
                                #print("in if")
                                flag=True
                                if not module:
                                    print("Bot:"+"You might want to check line number " +line_number
                                          +
                                          " in path  "+path_name)
                                    speak("You might want to check line number " +line_number
                                          +
                                          "in path  "+path_name)

                                else :
                                    print("Bot:"+"You might want to check line number "
                                          +line_number +" in path  "+path_name \
                                          +" in module  "+module)
                                    speak("You might want to check line number "
                                          +line_number +" in path  "+path_name \
                                          +" in module  "+module)


                                print("And full traceback/error is available "
                                      "for your reference in "
                                      "following file ",os.path.abspath(
                                    logfilename))
                            else:
                                print("else")
                                pass
                        else:
                            pass

