# Create your views here.
# Upload and read the file here taken EXCEL file into consideration
-------------------------------
@login_required
@group_required('superuser','engineer')
def FileUploadView(request):
    file_obj = models.Uploads.objects.count()
    files_list = list(models.Uploads.objects.values_list('File'))
    if request.method == 'POST':
        info = request.POST
        print(info)
        form = UploadFileForm(request.POST, request.FILES) #getting the file uploaded here
        print("Form",form)
        path = request.FILES['file']
        submitbutton= "Upload"
        print("Submit button", submitbutton)
        #print("form", form.data)
        if form.is_valid():
            
            upload_resource = UploadResource()
            dataset = Dataset()
            file = request.FILES['file'] # moving the file to a variable
            temp_file = file #to use the file in another view

            # #funtion to handle the file
            print("File uploaded")
            print("filename ", file)
            dbname = str(file).split('.') # split the file name at '.'
            print('dbname', dbname)
            filename_db = dbname[0] #file name saved in variable
            #print("file", file)
            try:
                chkbox_version = request.POST['version']
            except:
                chkbox_version = 'False'
            if chkbox_version == 'True':
                previous_version = request.POST['fname'] #Assigning the previous version file name to variable "previous_version"
                fileid = str(models.Uploads.objects.get(File = previous_version)).strip("Uploads object ()") #Getting the File ID of the previous version file str(fileid).strip("Uploads object ()")
            else:
                fileid = NULL
            document = models.Uploads(
                FilePath = path,
                File = filename_db,
                FileId = random.randrange(1000, 10000),
                File_VersionOf = fileid
            )
            
            document.save()
            r_file = document.FilePath.name
            print("r_file",r_file)
            new_fname = str(r_file).split("/")
            #print(new_fname)
            n_fname = new_fname[1].split(".")
            #print(n_fname)

            #Updating filename from the path
            up_fname = models.Uploads.objects.get(FilePath = r_file)
            up_fname.File = n_fname[0]
            up_fname.save()
            
            
            imported_data = dataset.load(file)
            columns = imported_data.headers
            
            context= {'filename': filename_db, 'columns':columns, 'submitbutton': submitbutton, 'file':file, 'file_details':r_file}
            print('context',context)
            
            return render(request, 'Files/fileupload.html', context)
            
        else:
            form = UploadFileForm()
            #return render(request, 'Files/fileupload.html', {'form': form})
        
    else:
        print("in else")
        file_dropdown = []
        filenames = []
        for i in range(file_obj):
            file_dropdown = str(files_list[i])
            #print(file_dropdown)
            filenames.append(file_dropdown.strip("(',)"))
            print("file_dropdown", filenames)
        form = UploadFileForm()
        context = {'dropdown':filenames,'form':form}
    return render(request, 'Files/fileupload.html', context)

  
# Show the fields of the file uploaded
@login_required

def Get_Columns(request):
    print("in get_col")
    form_b = GetColumns(request.POST)
    if request.method == "POST":
        columns_file_upload = request.POST # Reading the columns required for the file upload
        
    print("columns_file_upload:", columns_file_upload)
    filename = columns_file_upload['filename']
    print('file_path',filename)
    extracted_filename = filename.rpartition("/")
    print("extracted", extracted_filename)
    print(settings.MEDIA_ROOT)
    print("filename", extracted_filename[2])
    file_path = settings.MEDIA_ROOT+'\\'+filename
    print(file_path)
    
    file_1 = open(file_path,'rb')
    
    dataset1 = Dataset()
    file_data = dataset1.load(file_1,'xlsx')
    print("file data", file_data)
    
    col1 = columns_file_upload['req_text']
    col2 = columns_file_upload['target']
    col3 = columns_file_upload['req_id']
    col4 = columns_file_upload['assign_to']
    list_col = [col1,col2,col3,col4]
    file_pd = pd.read_excel(file_1)
    print(file_pd)
    max_rows = file_pd.shape[0]
    print(max_rows)
    row = 0
   
    data = file_data[col1]
    user_id = file_data[col3]
    target = file_data[col2]
    for row in range(len(data)):
        
        Requirement = models.Req(
                    ReqId = random.randrange(1000, 10000),
                    #Req_FromFile = extracted_filename,
                    FileId = models.Uploads.objects.get(FilePath = filename),
                    ReqText = data[row],
                    Req_UserId = user_id[row],                
                    
                )
        Requirement.save()
        print("req saved here")

    
        reqfile = models.ReqFiles(
            ReqFileID = random.randrange(1000, 10000),
            SrcId = models.Uploads.objects.get(FilePath = filename),
            Req_userid = user_id[row],
            TargetId = target[row],
            type = 0,
            Assign_To = col4,
        )
        reqfile.save()

    file_1.close()
    
    return render(request, 'Files/fileupload.html')

# show the data read and stored into database
@login_required

def Show(request):
    files = list(models.Uploads.objects.values_list('File'))
    count = models.Uploads.objects.count()
    print(count)
    print("objs in uploads",files)
    #form = getfilename(request.POST)
    if request.method == "POST":
        print(" in if")
        file = request.POST
        print(file)
        filename = file['fname']
        print(filename)
        #req = models.ReqFiles.objects.all()
        if filename == "all":
            
            countr = models.Req.objects.count()
            print("count",countr)
            reqfile = models.Req.objects.all()
            queryset = reqfile
            

        else:
            fileid = models.Uploads.objects.get(File = filename)
            print(fileid)
            countr = models.Req.objects.filter(FileId_id = fileid).count()
            print("count",countr)
            reqfile = models.Req.objects.filter(FileId_id = fileid)#.values_list()
            for row in range(countr):

                print(reqfile[row])
            queryset = reqfile
               
        p = Paginator(queryset,3)  # for 3 object per page
        #page_number = request.GET.get('page', 1)
        try:
            page_number = request.GET.get('page')
           
            page_object = p.page(page_number)
        except:
            page_object = p.page(1) 

        context = {
            'filename': filename,
            'requirements': reqfile,
            'users':page_object
        }
        return render(request,"Files/requirements_list.html",context)
    else:
        print("in else")
        
        file_dropdown = []
        filenames = []
        for i in range(count):
            file_dropdown = str(files[i])
            print("files in list",file_dropdown)
            print(i)
            filenames.append(file_dropdown.strip("(',)"))
            print("files", filenames)
    context = {'dropdown':filenames,}
    return render(request,"Files/requirements_list.html", context)

  
# To delete the file
@login_required    
@group_required('superuser','engineer')
def delete(request):
    file_obj = models.Uploads.objects.count()
    files_list = list(models.Uploads.objects.values_list('File'))
    if request.method == 'POST':
        print(request.POST)
        info = request.POST
        file_del = info['file_sel']
        fil_id = models.Uploads.objects.get(File=file_del)
        print(fil_id)
        file_id = str(fil_id).strip("Uploads object ()")
        print(file_id)
        fil = models.Uploads.objects.get(FileId=file_id)
        print(fil)
        
        fil_req = models.Req.objects.filter(FileId_id=file_id)
        print(fil_req)

        fil_req.delete() # delete from files_reqfiles
        
        fil.delete() # delete from files_req

        fil_id.delete() # delete from uploads

        messages.success(request, 'File deleted successfully!')
        print("in if")
        file_dropdown = []
        filenames = []
        for i in range(file_obj):
            file_dropdown = str(files_list[i])
            #print(file_dropdown)
            filenames.append(file_dropdown.strip("(',)"))
            print("file_dropdown", filenames)
        context = {'dropdown':filenames}
        return render(request,"Files/del_file.html",context)
    else:

        print("in else")
        file_dropdown = []
        filenames = []
        for i in range(file_obj):
            file_dropdown = str(files_list[i])
            #print(file_dropdown)
            filenames.append(file_dropdown.strip("(',)"))
            print("file_dropdown", filenames)

    context = {'dropdown':filenames}
    return render(request,"Files/del_file.html",context)
