import psutil
import platform
import time
import lsb_release
import time
from datetime import datetime
import csv
import os

def get_children():
    children=[]
    for pid in get_pid():
        process=psutil.Process(pid)
        if not process.children():
            continue
        else:
            children.append([pid,process.children()[0].name(),process.children()[0].pid])
    return children

def get_threads():
    threads=[]
    for pid in get_pid():
        process=psutil.Process(pid)
        if not process.threads():
            continue
        else:
            threads.append([pid,process.num_threads(),process.threads()[0][0]]) #Makes a list of [PID, NO OF THREADS OF THAT PID, ID OF THE THREAD]
    return threads

def get_pid():
    pid=[]
    for proc in psutil.process_iter(['name']): #code to fetch Process ID of application
                if proc.info['name']==name.lower():
                    pid.append(proc.pid)
                    pid=list(set(pid) & set(psutil.pids()))
    return (pid)

def get_python_app_cpu_usage(id):
    appcpu=0.0
    if not id:
        return "Error, please check if application is running"
    else:
        for i in id:
            proc=psutil.Process(i)
            appcpu+=round((proc.cpu_percent(interval=1)/psutil.cpu_count()),2)
        return appcpu
        
def get_overall_cpu_usage():
    return round(psutil.cpu_percent(),2)

def get_cpu_temperature():
    try:
    	return str(psutil.sensors_temperatures()["coretemp"][0].current)+'°C'
    except Exception as e:
        return(f"Error getting cpu temps: {e}")

def get_system_temperature():
   try:
        return str(psutil.sensors_temperatures()["nct6776"][0].current)+'°C'
   except Exception as e:
       return (f"Error getting system temps: {e}")

def get_python_app_ram_utilization(id):
        appram=0.0
        if not id:
            return "Error, check if application is running"
        else:
            for i in id:
                proc=psutil.Process(i)
                appram+=round(proc.memory_percent(),2)
            return round(appram,2)

def get_overall_ram_utilization():
    return round(psutil.virtual_memory().percent,2)

def get_ssd_status(): 
    hdd=psutil.disk_usage('/')
    total=round(hdd.total/(2**30),2)
    used=round(hdd.used/(2**30),2)
    free=round(hdd.free/(2**30),2)
    return {'Free Space (Gb)': free, 'Used Space(Gb)':used, 'Total Space(Gb)': total}

def get_ethernet_traffic():
    try:
        netdevices=[]
        net_stats = psutil.net_io_counters(pernic=True)
        for i in net_stats:
            #change name of network driver
            if i=='lo':
                continue
            else:
                netdevices.append( [i,(round((net_stats[i].bytes_sent)/float(2**20),2)),(round((net_stats[i].bytes_recv)/float(2**20),2))] ) 
        return netdevices
    except Exception as e:
        return (f"Error getting network traffic: {e}")


def main():
    while True: #print all list items properly, but write them directly into a csv file with a proper label
        p=get_pid()
        print("")
        print("Children of each instance: ")
        for z in get_children():
            print(f'Parent Process ID: {z[0]} --- Child Name: {z[1]} --- Child PID: {z[2]}') 
        print("")
        print("Thread of each instance: ")
        for x in get_threads():
            print(f'Process ID: {x[0]} --- No. of threads: {x[1]} ---  Thread PID: {x[2]}')  
        print("")             
        print("PythonAPP CPU Usage:", get_python_app_cpu_usage(p), "%")
        print("CPU Core Count: ",corecount)
        print("Overall CPU Usage:", get_overall_cpu_usage(),"%") 
        print("CPU Temperature:", get_cpu_temperature()) 
        print("System Temperature:", get_system_temperature()) 
        print("PythonAPP RAM Utilization:", get_python_app_ram_utilization(p),"%") 
        print("Overall RAM Utilization:", get_overall_ram_utilization(),"%") 
        print("SSD Status:", get_ssd_status())
        
        print("Network traffic:")
        
        for i in get_ethernet_traffic():
            print(f'DEVICE NAME: {i[0]} --- MB SENT: {i[1]} --- MB RECEIVED: {i[2]}')
        print("OS Info:", info) 
        print("\n--------------------------\n")
        
        now=datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        values=[get_children(),get_threads(),get_python_app_cpu_usage(p),get_overall_cpu_usage(),get_cpu_temperature(),get_system_temperature(),
                get_python_app_ram_utilization(p),get_overall_ram_utilization(),get_ethernet_traffic(),current_time]
        
        file_exists=os.path.isfile(filename)
        with open(filename, 'a') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(fields)
            writer.writerow(values)
        
        time.sleep(5)# Adjust the interval as needed

if __name__ == "__main__":
    
    filename= "RPRMS v1.0 "+ str(datetime.now())+".csv"
    
    fields=['Children of each instance[Parent PID, Process Name, Process PID]','Threads[Parent PID, No. of Threads, Thread ID ]','PythonAPP CPU Usage','Overall CPU Usage', 'CPU Temps', 
        'System Temps','PythonAPP RAM Utilisation','Overall RAM Utilisation','Network traffic, per device','Time']
    
    #code to fetch version information
    try:
        with open('/home/bsci/version') as f: #Enter directory of file here
            version=f.readline().strip('\n')
    except Exception as e:
        version=f"{e}"
    
    # code to fetch arbitrary system information
    
    info={'os_version': lsb_release.get_distro_information()['DESCRIPTION'],
        'kernel_version': platform.uname().release,
        'application': version}
    name=input("Enter process name:")
    corecount=psutil.cpu_count()
    
    #main driver loop
    main()

