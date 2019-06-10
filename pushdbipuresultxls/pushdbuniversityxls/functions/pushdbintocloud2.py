def PushDatabaseinCloudfromuniverityXLS(Path):
    import pandas as pd 
    DF=pd.read_excel(Path)
    import xlrd
    workBook = xlrd.open_workbook(Path)
    sheet= workBook.sheet_by_index(0)
    ROWS = sheet.nrows
    COLUMNS =sheet.ncols
    KeysNameforComonInformation=[]
    TotalNumberofSubject=0
    for col in range(1,13):
        KeysNameforComonInformation.append(sheet.cell_value(0,col))
    TotalNSL=[]

    for col in range(13,COLUMNS):
        TotalNSL.append(sheet.cell_value(0,col))
    TotalNumberSubject=int(len(TotalNSL)/9)
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
        for i in range(13):
            Ans.append(L[i])
        return Ans
    def CreateSubjectRow(L):
        ans=[]
        TotalSubject=int((len(L)-13)/9)
        Indexes=[]
    #     print(TotalSubject)
        for i in range(TotalSubject):
            Indexes.append((13)+(9*i))

        Indexes.append(Indexes[-1]+9)

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
#         print('ans = ',ans)
#         print('L = ',L)
        for i in L:
            if(len(i[0])>0):
                L2.append(i)
        ans.append(L2)
#         print(L2)
        return ans
    NewLLforMongo=[]
    for i in AfterLabelingCreateL:
        NewLLforMongo.append(RemoveVacentSubjectL(i))
    import pymongo
    from pymongo import MongoClient
    Client = pymongo.MongoClient('localhost',27017)
#     Client = pymongo.MongoClient('mongodb://jatinanand345:jatin#123@ds357955.mlab.com:57955/evaluationsystemdb')
    db =  Client.resultconsolidatesystemdb
#     db = Client.evaluationsystemdb
    students = db.nstudents
    def CreateSubjectDatawithData(L,examinationtype):
        ans={}
        ans['obtainedcredit']=L[6]
        ans['internalm']=L[7]
        ans['external']=L[-1]
        ans['examinationtype']=examinationtype
        return ans

        
    def CreateOneSubjectDict(L,declaredate,examinationtype):
        creditL=L[4]
        key=L[1]
        externalL = L[-1]
        Ans={}
        Ans={'subjectid':L[0],'subjectname':L[2],'subjecttype':L[3],'totalcredit':creditL,'subjectkind':L[5]}
        Ans['internalm1']=0
        Ans['internalm2']=0
        Ans['internalm3']=0
        Ans['internalm4']=0
        Ans['internalm5']=0
        Ans['markswithdate']={}
        Ans['markswithdate'].update({declaredate:CreateSubjectDatawithData(L,examinationtype)})
        return Ans
    def CreateDictforSemesterNumber(L,DB,declaredate,examinationtype):
        SameIDL=[]
        for i in L:
            DB.update({i[1]:CreateOneSubjectDict(i,declaredate,examinationtype)})
        return DB
    def CreateBSONobjectMongoDB(L,DB):
        Ans={}
        keysNew =['semester', 'enrollmentnumber', 'name', 'schemaid', 'sid']
        Ans['enrollmentnumber']=L[0][0]
        Ans['name']=L[0][1]
        Ans['sid']=L[0][2]
        Ans['schemaid']=L[0][3]
        s=L[0][4]
        declaredate = L[0][5]
        examinationtype = L[0][8]
        Ans['batch']=L[0][6]
        Ans['classrollnumber']=L[0][7]
        Ans['institutecode']=L[0][9]
        Ans['institutename']=L[0][10]
        Ans['programmecode']=L[0][11]
        Ans['programmename']=L[0][12]
        Ans['semester']={}
        Ans['semester'].update({s:CreateDictforSemesterNumber(L[-1],{},declaredate,examinationtype)})
        DB.insert_one(Ans)
        return 0
    def UpdateMarkswithDate(i,j,DB,declaredate,examinationtype):
#         print('I = ',i)
#         print('J = ',j)
#         print('Previous Subject dict = ',DB[j])
        DB[j]['markswithdate'].update({declaredate:CreateSubjectDatawithData(i,examinationtype)})
#         print('After Subject dict = ',DB[j])
        return DB
    
    def CreateDictforAlreadySemesterNumber(L,DB,declaredate,examinationtype):
#         print("Updated data = ",L)
#         print('previous dict = ',DB)
        KEYSofSubject = list(DB.keys())
#         print('Semester Keys = ',KEYSofSubject)
#         print(declaredate,examinationtype)
        for i in L:
            for j in KEYSofSubject:
                if(i[1].find(j)>-1):
                    DB[j]['markswithdate'].update({declaredate:CreateSubjectDatawithData(i,examinationtype)})
#                     UpdateMarkswithDate(i,j,DB,declaredate,examinationtype)
                    break
        return DB
#         
        
    def UpdateBSONobjectMongoDB(L,DB):
        query={'enrollmentnumber':L[0][0]}
        StudentPreviousBson = DB.find_one(query)
        InputSemesterNumber = L[0][4]
        StudentPreviousSemesterDict= StudentPreviousBson['semester']
        declaredate = L[0][5]
        examinationtype = L[0][8]        
        LkeysSemster=list(StudentPreviousSemesterDict.keys())
        ans=0
        f1=0
        for i in LkeysSemster:
            if(i.find(InputSemesterNumber)>-1):
                f1=1
                break
        if(f1==1):
            StudentPreviousSemesterNumberDict = StudentPreviousSemesterDict[InputSemesterNumber]
            StudentUpdatedSemesterNumberDict = CreateDictforAlreadySemesterNumber(L[1],StudentPreviousSemesterNumberDict,declaredate,examinationtype)
            StudentPreviousSemesterDict.update({InputSemesterNumber:StudentUpdatedSemesterNumberDict})
            StudentPreviousBson.update({'semester':StudentPreviousSemesterDict})
#             print('Updated DIct  = ',StudentPreviousBson)
            newvalues= {"$set":StudentPreviousBson}
            DB.update_one(query,newvalues)
            ans=2
        else:
            StudentPreviousSemesterDict.update({InputSemesterNumber:CreateDictforSemesterNumber(L[1],{},declaredate,examinationtype)})
            StudentPreviousBson.update({'semester':StudentPreviousSemesterDict})
#             print(StudentPreviousBson)
            newvalues= {"$set":StudentPreviousBson}
            DB.update_one(query,newvalues)
            ans=1
        return ans
    def FillDatainMongoDBObject(L,DB):
        query={'enrollmentnumber':L[0][0]}
        f1=0
        NoneType = type(None)
        StudentDict = DB.find_one(query)
#         print(StudentDict)
        if(type(StudentDict)==NoneType):
            if(CreateBSONobjectMongoDB(L,DB)==0):
                f1=1
        else:
            if(UpdateBSONobjectMongoDB(L,DB)>0):
                f1=2
        return f1 
#     FillDatainMongoDBObject(NewLLforMongo[0],students)
    for i in NewLLforMongo:
        FillDatainMongoDBObject(i,students)
    return 'DONE'

 

    