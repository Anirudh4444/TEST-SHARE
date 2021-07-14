# Call to jenkins job
import traceback
import urllib3
import jenkins
import pyttsx3
import tkinter as tk
import requests
import sys
import time
from win10toast import ToastNotifier
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# secs for polling Jenkins API
#
QUEUE_POLL_INTERVAL = 2
JOB_POLL_INTERVAL = 5
OVERALL_TIMEOUT = 3600 # 1 hour

engine = pyttsx3.init('sapi5')

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def get_url():
    def monitor ():
        global url,jenkins_username,jenkins_secret,job_name
        url = e1.get()
        jenkins_username=e2.get()
        speak("Triggering Jenkins job")
        print("Bot :"+" Connecting to Jenkins")
        jenkins_secret=e3.get()
        master.destroy()
        job_name=url.split("/")
        i=next(i for i in reversed(range(len(job_name))) if job_name[i] ==
               'job')

        job_name=job_name[i+1] if 'job' in job_name else print(
            "Job name not found")

        global build_num
        url=url.rsplit("/",3)[0]+"/"

        build_num=triggerJenkins(job_name,url, jenkins_username,
                       jenkins_secret)
        if build_num != -1:
            monitor_result(url,job_name,build_num,jenkins_username, jenkins_secret)
    master = tk.Tk()
    master.geometry("400x250")

    tk.Label(master,
             text="Jenkins job url ").grid(row=0)
    tk.Label(master,
             text="Username").grid(row=1)
    tk.Label(master,
             text="Password").grid(row=2)
    tk.Button(master,
              text='Trigger and Monitor', command=monitor).grid(row=3,column=1,
                                                      sticky=tk.W,
                                                    pady=4)
    # url='https://st-devnetops.acndevopsengineering.com/jenkinscore/job/devnetops_pipeline/job/onboard_management/'
    # username='ethanadmin'
    # password='hbzYjGvWuioQJaln00'
    # url='http://localhost:8080/job/job1/'
    url='https://build-env.acndevopsengineering.com/jenkinscore/job/devnetops/job/Devnetops_modules/job/role-delete/'
    username='ethanadmin'
    password='DQLqEc9Neh86lazm28'

    e1 = tk.Entry(master)
    e1.insert(-1, url)
    #    e1.pack()
    e2 = tk.Entry(master,show="*")
    e2.insert(-1, username)
    #   e2.pack()
    e3 = tk.Entry(master,show="*")


    e3.insert(-1, password)
    #  e3.pack()

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)


    master.mainloop()
# """Verifies Jenkins authentication and establish connection""
def make_jenkins_connection(jenkins_url, jenkins_username, jenkins_secret):
    try:
        jenkins_obj = jenkins.Jenkins(jenkins_url, jenkins_username,
                                      jenkins_secret)
        #print("Jenkins connection established")
        return jenkins_obj
    except Exception as e:
        print("Bot:"+"Unable to establish jenkins connection")
        speak("Unable to establish jenkins connection")
        exit()



# """Gets list of all the jenkins job"""
def get_job_details(url, jenkins_username, jenkins_secret):
    def job_list(dict_var):
        for item in dict_var:
            if item['_class'] == 'org.jenkinsci.plugins.workflow.job.WorkflowJob':
                yield item['fullname']
            elif item['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
                for ret_val in job_list(item['jobs']):
                    yield ret_val
    try:
        jenkins_obj = make_jenkins_connection(
            url, jenkins_username, jenkins_secret)
        job_details = jenkins_obj.get_all_jobs()
        if job_details:

            return [_ for _ in job_list(job_details)]
    except Exception as e:
        speak("Unable to trigger jenkins job")
        print("Bot: "+"Unable to trigger jenkins job")
        exit()
        # print(traceback.format_exc())
        # print(e)



"""get job jenkins console logs"""


def get_job_logs(job_name, build_id):
    try:
        jenkins_obj = make_jenkins_connection(
            url, jenkins_username, jenkins_secret)
        job_logs = jenkins_obj.get_build_console_output(job_name, build_id)
        return job_logs
    except Exception as e:
        print("Bot: "+"Unable to fetch job logs")
        exit()
        # print(traceback.format_exc())
        # print(e)

# """Triggers jenkins job build with build specific parameters"""


def triggerJenkins(job_name,jenkins_url, jenkins_username,
                   jenkins_secret,parameters=None):
    try:
        #print("trigger",job_name,jenkins_url, jenkins_username,jenkins_secret)
        jenkins_obj = make_jenkins_connection(
            jenkins_url, jenkins_username, jenkins_secret)
        # """Triggering jenkins build"""
        job_list = get_job_details(jenkins_url, jenkins_username, jenkins_secret)
        if job_list:
            if job_name in job_list:
                queue_id = jenkins_obj.build_job(job_name, parameters)
                while True:
                    queue_details = jenkins_obj.get_queue_item(queue_id)
                    if 'executable' in queue_details:
                        build_num = jenkins_obj.get_queue_item(
                            queue_id)['executable']['number']
                        break
                    time.sleep(1)
                speak("Build triggered for job")
                print("Bot: "+"Build triggered for job")
                return build_num
            else:
                speak("Unable to trigger jenkins job,invalid job name")
                print("Bot: "+"Unable to trigger jenkins job,invalid job name")
                #print(traceback.format_exc())
                return -1

    except Exception as e:
        speak("Unable to trigger jenkins job")
        print(e)
        print("Bot: "+"Unable to trigger jenkins job")
        return -1
        # print(traceback.format_exc())
        # print(e)
def monitor_result(url,job_name,build_num,jenkins_username,jenkins_secret):
    # poll job status waiting for a result
    #
    job_url = '{}job/{}/{}/api/json'.format(url, job_name,
                                                       build_num)
    #print("==========",job_url)
    print("Bot: "+"Monitoring job...")
    speak("Monitoring job...")
    start_epoch = int(time.time())
    while True:
        print ("{}: Job started URL: {}".format(time.ctime(), job_url))
        j = requests.get(job_url,auth=(jenkins_username,
                                       jenkins_secret),verify=False)
        jje = j.json()
        result = jje['result']
        if result == 'SUCCESS':
            # Do success steps
            print ("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            toaster = ToastNotifier()
            speak("Your jenkins job status is:"+result.lower())
            toaster.show_toast(result,"Jenkins Job Status!",
                               duration=5)
            #print(status,job_name,resp.json()['number'])
            break

        elif result == 'FAILURE':
            # Do failure steps
            speak("Your jenkins job status is:"+result.lower())
            toaster = ToastNotifier()
            toaster.show_toast(result,"Jenkins Job Status!",
                               duration=5)
            print ("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            log_url=url+"job/"+job_name+"/"+"lastBuild/consoleText"
            #print(log_url)

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            job_logs=requests.get(log_url,verify=False,auth=(jenkins_username,
                                                             jenkins_secret)).text
            #job_logs = jenkins_obj.get_build_console_output(job_name,
            # resp.json()['number'])
            #print(job_logs)
            error=job_logs.splitlines()
            error=error[error.index('[Pipeline] End of Pipeline')+1]
            print("Bot:"+"Jenkins job failed with error: \n "+error)
            speak("Bot:"+"Jenkins job failed with error!!!!"+error)
            break
        elif result == 'ABORTED':
            # Do aborted steps
            print ("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            toaster = ToastNotifier()
            speak("Your jenkins job status is:"+result.lower())
            toaster.show_toast(result,"Jenkins Job Status!",
                               duration=5)
            print ("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            break
        else:
            print ("{}: Job: {} Status: {}. Polling again in {} secs".format(
                time.ctime(), job_name, result, JOB_POLL_INTERVAL))

        cur_epoch = int(time.time())
        if (cur_epoch - start_epoch) > OVERALL_TIMEOUT:
            print ("{}: No status before timeout of {} secs".format(
                OVERALL_TIMEOUT))
            sys.exit(1)

        time.sleep(JOB_POLL_INTERVAL)