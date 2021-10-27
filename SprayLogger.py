import csv
import sys
import io
from datetime import datetime

#class CsvFormatter(logging.Formatter):
class CsvFormatter:
    def __init__(self):
        print("SUPER: {}".format(super()))
        super().__init__()
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)
        
    def format(self, record):
        dtString, message = record.msg
        self.writer.writerow([record.levelname, dtString, message])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()

class SprayLogger():     
    
    def __init__(self, output_file, log_level=None):
        self.message = ''
        self.out = None    
        self.output_file = output_file
        sys.stdout.write("[+] Set output file to {}\n".format(output_file))
        self.logging = __import__('logging')
        
        if not log_level:
            self.log_level = self.logging.DEBUG
        else:
            self.log_level = log_level                    
        
        self.logging.basicConfig(level=self.logging.DEBUG,
                                filename=output_file)
        self.logging.root.handlers[0].setFormatter(CsvFormatter())
                               
    def log(self, message):     
        if not self.out:
            if not self.output_file:
                now = datetime.now().strftime("%m/%d/%Y-%H-%M-%S")
                self.output_file = ("{}.txt".format(now))
                self.start()
        self.append_log(message)

    def start(self):
        if self.output_file and not self.out:
            self.open_logfile(self.output_file)
        self.append_log("Started Logging",'info')           
    
    def stop(self):
        if self.out:
            self.out.close()        
            self.append_log("Stopped Logging",'info')

    def append_log(self,message,log_type='INFO'):
        date_time = (datetime.now()).strftime("%m/%d/%Y-%H:%M:%S") 
        getattr(self.logging,'info')([date_time,message])

        #self.output_file.write(message)
    def open_logfile(self,output_file):
        try:
            handler = self.logging.FileHandler(output_file)
            self.logging.addHandler(handler)
            #self.out = open(output_file, 'a')        
        except:
            sys.stdout.write("[-] Failed to set file handler.")