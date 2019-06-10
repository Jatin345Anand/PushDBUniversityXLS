# from odo.chunks import chunks


def handle_uploaded_file(f):
    print('In functions and file is ',f)
    with open('pushdbuniversityxls/static/upload/'+f.name,'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)