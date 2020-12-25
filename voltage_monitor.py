'''
TADAHCORP.COM
version 1.2
PURPOSE:
    Displays voltage or temperature issues on a Raspberry Pi
USAGE:
    invoke, optionally passing an interval in seconds (or fractions) -- default 1
OUTPUT:
    Single line black and white overwriting itself (with timer)
    or
    Line in RED showing date-time and explanation of the issue (not overlapping)
REQUIREMENTS:
    vcgencmd 
    colorama (optional)

0 	Under-voltage detected
1 	Arm frequency capped
2 	Currently throttled
3 	Soft temperature limit active
16 	Under-voltage has occurred
17 	Arm frequency capping has occurred
18 	Throttling has occurred
19 	Soft temperature limit has occurred

UPDATES
- now not showing in red or counting as error the "occurred" 16..19
- store and display after normal the datetime last error

'''
import sys,time,datetime
from os.path import isfile

# hardwired change to wherever you wish to write the log
filename = "/home/pi/voltage_monitor.csv"

try:
    from vcgencmd import Vcgencmd
except Exception as e:
    print("library missing: issue the command 'pip3 install vcgencmd' and retry")
    sys.exit() 

try:
    from colorama import Fore, Back, Style, init
    hascolor = True
except Exception as e:
    print("library missing: issue the command pip3 install colorama")
    hascolor = False
try:
    import csv  
    haslogging = True
    # field names  
    fields = ["timestamp", "under_voltage_detected","arm_frequency_capped","currently_throttled","soft_temp_limit","under_voltage_occurred","arm_frequency_capping_occurred","throttling_occurred","soft_temp_occurred"]
    
    if isfile(filename):
        csvfile = open(filename,'a')
        csvwriter = csv.writer(csvfile,dialect='excel')  
        print("appending logs to: " + filename)
    else:
        csvfile = open(filename,'w')
        csvwriter = csv.writer(csvfile,dialect='excel')  
        csvwriter.writerow(fields) 
        print("logging to: " + filename)
except Exception as e:
    print("if you want to log you are missing a library: issue the command pip3 install csv")
    print(str(e))
    haslogging = False

def write_log(arow):    
    # writing the data rows  
    try:
        csvwriter.writerow(arow) 
        # print("logged",arow)
        # commit to drive
        csvfile.flush()
    except Exception as e:
        print("not logged: " + str(e))

def get_date():
    now_date = datetime.datetime.now()
    datetime_string = now_date.strftime("%H:%M:%S")
    return datetime_string

def get_datetime():
    now_date = datetime.datetime.now()
    datetime_string = now_date.strftime("%b %d %Y %H:%M:%S")
    return datetime_string

vcgm = Vcgencmd()
try:
    interval = float(sys.argv[1])
    print("running at an interval of " + str(interval) + " seconds.")
except Exception as e:
    print(str(e))
    print("note: you can pass the loop interval as a value in seconds, e.g. voltage_check.py 0.5")
    interval = 1

num_errors = 0
last_error = ""

while True:
    status = []
    row = [get_date(),0,0,0,0,0,0,0,0]
    sum_bits = 0
    output = vcgm.get_throttled()
    if "breakdown" in output:
        result = output["breakdown"]
        # testing
        # result = {'0': False, '1': False, '2': True, '3': False, '16': True, '17': False, '18': False, '19': False}
        if result['0'] == True: 
            row[1]=1
            sum_bits += 1
            status.append(fields[1])
            last_error = "(last err since boot under VDC: " + get_datetime() + ")"
        if result['1'] == True:
            row[2]=1
            sum_bits += 1
            status.append(fields[2])
            last_error = "(last err since boot arm freq cap: " + get_datetime() + ")"
        if result['2'] == True:
            row[3]=1
            sum_bits += 1
            status.append(fields[3])
            last_error = "(last err throttled: " + get_datetime() + ")"
        if result['3'] == True:
            row[4]=1
            sum_bits += 1
            status.append(fields[4])
            last_error = "(last err temp limit: " + get_datetime() + ")"
        if result['16'] == True:
            row[5]=1
            # sum_bits += 1
            status.append(fields[5])
        if result['17'] == True:
            row[6]=1
            # sum_bits += 1
            status.append(fields[6])
        if result['18'] == True:
            row[7]=1
            # sum_bits += 1
            status.append(fields[7])
        if result['19'] == True:
            row[8]=1
            # sum_bits += 1
            status.append(fields[8])
    # print("row",row)        
    if sum_bits == 0:
        print('\r', get_date() + ": normal " + last_error, sep='', end='', flush=True)
    else:
        num_errors += 1
        if hascolor == True:
            print("\n",f"{Fore.GREEN}{Back.RED}" + "Err #" + f"{Style.RESET_ALL}" + str(num_errors) + " at " + get_date() + ": " + ','.join(status), sep='', end='',flush=True)
        else:
            print("ERR: " + get_date() + ": " + ','.join(status))
        if haslogging == True:
            write_log(row)
    time.sleep(interval)
