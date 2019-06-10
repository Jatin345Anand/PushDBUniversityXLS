 

# Create your views here.

from django.shortcuts import render
from pushdbuniversityxls.functions.functions import handle_uploaded_file
from pushdbuniversityxls.functions.pushdbintocloud2 import PushDatabaseinCloudfromuniverityXLS
# from pushdbuniversityxls.functions.pushdatabasefromuniversityxls import PushDatabaseinCloudfromuniverityXLS 
# Create your views here.
import os


def index(req):
    samplepath = ''
    pushstatus = ''
    if req.method == "POST":
        print('Index Form Data = ', req.POST)
        if(len(req.FILES) > 0):
            print('Index Form File Data = ', req.FILES,
                  len(req.FILES), type(req.FILES))
            print('Input file data 2 =',
                  req.FILES['updf'], type(req.FILES['updf']))
            FileName =  req.FILES['updf']

            print('Index Form File Input of write stream = ',type(FileName))
            handle_uploaded_file(FileName)
            print('done...')
            FileName = str(FileName)
            if(len(FileName) > 0 and (FileName.find('.xls') > -1 or FileName.find('.xlsx') > -1)):
                InputPath = os.getcwd()+'/pushdbuniversityxls/static/upload/'+str(FileName)
                print('Your Input path file = ', InputPath)
                pushstatus = PushDatabaseinCloudfromuniverityXLS(InputPath)
                print('Push status = ', pushstatus)
                FileName = str(FileName)
                samplepath = str('../static/output/sampleuniverity.xls')
                print('New DownloadPath = ', samplepath)
    else:
        print('Your method is not POST....')
        # FuploadPDF = UploadFiles()

    return render(req, 'index.html', {'downloadpath':  samplepath, 'pushstatus': pushstatus})


def samplef(req):
    print('Sample Format data  = ', req.POST)
