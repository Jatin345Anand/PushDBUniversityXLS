def PushDatabaseinCloudfromuniverityXLS(Path):
    print('start')
    import pandas as pd 
    DF=pd.read_excel(Path)
    import xlrd
    workBook = xlrd.open_workbook(Path)
    sheet= workBook.sheet_by_index(0)
    ROWS = sheet.nrows
    COLUMNS =sheet.ncols
    KeysNameforComonInformation=[]
    TotalNumberofSubject=0
    for col in range(1,12):
        KeysNameforComonInformation.append(sheet.cell_value(0,col))
    TotalNSL=[]

    for col in range(12,COLUMNS):
        TotalNSL.append(sheet.cell_value(0,col))
    TotalNumberSubject=int(len(TotalNSL)/10)
    LLforDB=[]
    def FindRowData(i):
        ans=[]
        for col in range(1,COLUMNS):
            ans.append(sheet.cell_value(i,col))
        return ans

    for i in range(1,ROWS):
        LLforDB.append(FindRowData(i))
    def CreateListforSubject(ML,i1,i2):
        Ans=[]
        while(i1<i2):
            Ans.append(ML[i1])
            i1 += 1
        return Ans

    def CreateCommonInformation(L):
        Ans=[]
        for i in range(11):
            Ans.append(L[i])
        return Ans
    def CreateSubjectRow(L):
        ans=[]
        TotalSubject=int((len(L)-11)/10)
        Indexes=[]
        for i in range(TotalSubject):
            Indexes.append((11)+(10*i))
        Indexes.append(Indexes[-1]+10)
        for i in range(len(Indexes)-1):
            ans.append(CreateListforSubject(L,Indexes[i],Indexes[i+1]))
        return ans
    def CreateAllLabaledData(L):
        ans=[]
        ans.append(CreateCommonInformation(L))
        ans.append(CreateSubjectRow(L))
        return ans
    AfterLabelingCreateL=[]
    for i in range(len(LLforDB)):
        AfterLabelingCreateL.append(CreateAllLabaledData(LLforDB[i]))
    def RemoveVacentSubjectL(L1):
        L=L1[1]
        ans =[]
        L2=[]
        ans.append(L1[0])
        for i in L:
            if(len(i[0])>0):
                L2.append(i)
        ans.append(L2)  
        return ans
    NewLLforMongo=[]
    for i in AfterLabelingCreateL:
        NewLLforMongo.append(RemoveVacentSubjectL(i))
    
    import pymongo
    from pymongo import MongoClient
    Client = pymongo.MongoClient('localhost',27017)
    # Client = pymongo.MongoClient('mongodb://jatinanand345:jatin#123@ds357955.mlab.com:57955/evaluationsystemdb')
    db =  Client.evaluationsystemdb
    students = db.nstudents
    import random
    def CreateRandomNumber(n,n1,n2,n3):
        L1=[]
        L2=[]
        L3=[]
        Ans=[]
    #     print('n = ',n)
        for i in range(n1):
            L1.append(random.randint(i,n1))
        for i in range(n2):
            L2.append(random.randint(i,n2))
        for i in range(n3):
            L3.append(random.randint(i,n3))
    #     print('in random number...',n,n1,n2,n3,len(L1),len(L2),len(L3))
        for i in L1:
            for j in L2:
                for k in L3:
                    if((i+j+k)== n ):
    #                     print('i = ',i,'j = ',j,'k = ',k,'sum = ',(i+j+k))
                        Ans.append(i)
                        Ans.append(j)
                        Ans.append(k)
                        return Ans,i,j,k

    def CreateOneSubjectDict(L):
#         print(' one subject L ',L)
        creditL=L[4]
        key=L[0]

        externalL = L[-1]
        Ans={}
    #     if('A' not in L[2]):
    #         if(int(L[2])<26):
    #             interL=[]
    #             internalL=int(L[2])

    # #             interL = CreateRandomNumber(internalL,15,5,5)[0]
    # #             print(interL)
    # #             in1 = interL[1]
    # #             in2 = interL[-1]
    # #             in3 = interL[0]
    # #             Ans={'credit':creditL,'internal':str(internalL),'internal1':str(in1),'internal2':str(in2),'internal3':str(in3),'external':externalL}
    #         else:
    #             Ans={'credit':creditL,'internal':L[2],'internal1':'0','internal2':'0','internal3':'0','external':externalL}


    #     else:
    #         Ans={'credit':creditL,'internal':L[2],'internal1':'0','internal2':'0','internal3':'0','external':externalL}
        Ans={'pepercode':L[1],'pepername':L[2],'pepertype':L[3],'credit':creditL,'internal':L[5],'internal1':'0','internal2':'0','internal3':'0','external':externalL}
    #     print(Ans)   
        return Ans

    def CreateDictforSemesterNumber(L,DB):
        SameIDL=[]
        for i in L:
#             print(' i = ',i)
            DB.update({i[0]:CreateOneSubjectDict(i)})
        return DB

    def UpdateBSONobjectMongoDB(L,DB):
        query={'enrollmentnumber':L[0][0]}
        StudentPreviousBson = DB.find_one(query)
        InputSemesterNumber = L[0][4]
        StudentPreviousSemesterDict= StudentPreviousBson['semester']
        LkeysSemster=list(StudentPreviousSemesterDict.keys())
        ans=0
        f1=0
        for i in LkeysSemster:
            if(i.find(InputSemesterNumber)>-1):
                f1=1
                break
        if(f1==1):
            StudentPreviousSemesterNumberDict = StudentPreviousSemesterDict[InputSemesterNumber]
            StudentUpdatedSemesterNumberDict = CreateDictforSemesterNumber(L[1],StudentPreviousSemesterNumberDict)
            StudentPreviousSemesterDict.update({InputSemesterNumber:StudentUpdatedSemesterNumberDict})
            StudentPreviousBson.update({'semester':StudentPreviousSemesterDict})
            newvalues= {"$set":StudentPreviousBson}
            DB.update_one(query,newvalues)
            ans=2
        else:
            StudentPreviousSemesterDict.update({InputSemesterNumber:CreateDictforSemesterNumber(L[1],{})})
            StudentPreviousBson.update({'semester':StudentPreviousSemesterDict})
            newvalues= {"$set":StudentPreviousBson}
            DB.update_one(query,newvalues)
            ans=1
        return ans
    def DeleteBSONobjectMongoDB(L,DB):
        f1=0
        query={'enrollmentnumber':L[0][0]}
        DB.delete_one(query)
        f1=1
        return f1


    def CreateBSONobjectMongoDB(L,DB):
        Ans={}
        keysNew =['semester', 'enrollmentnumber', 'name', 'schemaid', 'sid']
        Ans['enrollmentnumber']=L[0][0]
        Ans['name']=L[0][1]
        Ans['sid']=L[0][2]
        Ans['schemaid']=L[0][3]
        s=L[0][4]
        Ans['batch']=L[0][5]
        Ans['classrollnumber']=L[0][6]
        Ans['institutecode']=L[0][7]
        Ans['institutename']=L[0][8]
        Ans['programmecode']=L[0][9]
        Ans['programmename']=L[0][10]
        Ans['semester']={}
        Ans['semester'].update({s:CreateDictforSemesterNumber(L[-1],{})})
        DB.insert_one(Ans)
        return 0



    def FillDatainMongoDBObject(L,DB):
        query={'enrollmentnumber':L[0][0]}
        f1=0
        NoneType = type(None)
        StudentDict = DB.find_one(query)
        if(type(StudentDict)==NoneType):
            if(CreateBSONobjectMongoDB(L,DB)==0):
                f1=1
        else:
            if(UpdateBSONobjectMongoDB(L,DB)==0):
                f1=2
        return f1 
    # FillDatainMongoDBObject(AfterLabelingCreateL[0],students)
    for i in NewLLforMongo:
#         print(i)
    # #     print(i[0][0])
        FillDatainMongoDBObject(i,students)
    print('end')
    return 'DONE'
    