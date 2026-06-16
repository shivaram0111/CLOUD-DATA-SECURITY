from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import userreg, Encryptedmodel, Filerequestmodel
import random
import os
from django.conf import settings
from django.core.mail import send_mail
from .aes import encrypt, decrypt
from .ecc import fernet_key

# Template Variables
INDEXPAGE = "index.html"
loginpage = 'login.html'
regpage = 'reg.html'
viewowneracpt = 'viewalluser.html'
cloudhomepage = 'cloudhome.html'
userhomepage = 'userhome.html'
ENCRYPTDATAPAGE = "encrypt.html"
VIEWFILESPAGE = "viewfiles.html"
FILEREQUESTPAGE = "filerequest.html"
SENDKEYPAGE = "sendkey.html"
DECRYPTPAGE = "decryptpage.html"
VIEWMYFILESPAGE = "viewmyfiles.html"
VIEWCLOUDFILESPAGE = "cloudfile.html"
VIEWFILESREQUESTPAGE = 'filerequestcloud.html'

def index(req):
    return render(req, INDEXPAGE)

def login(request):
    if request.method == "POST":
        login_type = request.POST.get('login_type')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not login_type or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, loginpage)
            
        if login_type == "cloudserver":
            if email == "cloud@gmail.com" and password == "cloud":
                request.session['email'] = email
                request.session['name'] = 'Cloud Server Admin'
                return render(request, cloudhomepage)
            else:
                messages.error(request, 'Invalid cloud server credentials.')
                return render(request, loginpage)
                
        elif login_type == "user":
            try:
                user = userreg.objects.get(email=email, password=password, status='Activated')
                request.session['email'] = user.email
                request.session['name'] = user.name
                request.session['useremail'] = user.email
                return render(request, userhomepage, {'userdata': user})
            except userreg.DoesNotExist:
                messages.error(request, "Invalid user credentials or account not activated.")
                return render(request, loginpage)
        else:
            messages.error(request, "Invalid login type selected.")
            return render(request, loginpage)
            
    return render(request, loginpage)

def user(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conpasword = request.POST.get('password2')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        
        if password == conpasword:
            data_exists = userreg.objects.filter(email=email).exists()
            if not data_exists:
                data_insert = userreg(name=name, email=email, password=password, contact=contact, address=address)
                data_insert.save()
                messages.success(request, 'Registered successfully.')
                return render(request, loginpage)
            else:
                messages.warning(request, 'Details already exist.')
                return redirect("user")
        else:
            messages.warning(request, 'Passwords do not match.')
            return render(request, regpage)
    return render(request, regpage)

def userhome(request):
    if 'useremail' not in request.session:
        return redirect('login')
    
    user = userreg.objects.get(email=request.session['useremail'])
    return render(request, userhomepage, {'userdata': user})

def cloudhome(req):
    if req.session.get('name') != 'Cloud Server Admin':
        return redirect('login')
    activated_users = userreg.objects.filter(status='Activated')
    user_count = activated_users.count()
    return render(req, cloudhomepage, {'activated_users': activated_users, 'user_count': user_count})

def viewusers(request):
    if request.session.get('name') != 'Cloud Server Admin':
        return redirect('login')
    usersdata = userreg.objects.filter(status='Deactivated')
    return render(request, viewowneracpt, {'usersdata': usersdata})

def acceptuser(request, id):
    if request.session.get('name') != 'Cloud Server Admin':
        return redirect('login')
    data = userreg.objects.get(id=id)
    data.status = 'Activated'
    data.save()
    messages.success(request, f'The User "{data.name}" has been successfully activated.')
    return redirect("viewusers")

def viewcloudfiles(req):
    if req.session.get('name') != 'Cloud Server Admin':
        return redirect('login')
    encrypted_data = Encryptedmodel.objects.all()
    return render(req, VIEWCLOUDFILESPAGE, {'encrypted_data': encrypted_data, 'file': 'nofile'})

def viewfilesrequest(req):
    if req.session.get('name') != 'Cloud Server Admin':
        return redirect('login')
    data = Filerequestmodel.objects.all()
    encrypted_data = Encryptedmodel.objects.all()  # Get all encrypted files to match with requests
    return render(req, VIEWFILESREQUESTPAGE, {'filedata': data, 'encrypted_data': encrypted_data})


def acceptfilerequest(req, id):
    if req.session.get('name') != 'Cloud Server Admin':
        return redirect('login')
    try:
        fr = Filerequestmodel.objects.get(id=id)
        fr.status = 'approved'
        fr.save()
        messages.success(req, 'File request approved successfully.')
    except Filerequestmodel.DoesNotExist:
        messages.error(req, 'File request not found.')
    return redirect('viewfilesrequest')

def encryptdata(req):
    if 'useremail' not in req.session:
        return redirect('login')
    if req.method == "POST":
        algorithm = req.POST['algorithm']
        
        # Check if it's a file upload or text message
        if 'file' in req.FILES:
            # File upload
            uploaded_file = req.FILES['file']
            file_content = uploaded_file.read()
            filename = uploaded_file.name
            filetype = 'file'
        else:
            # Text message
            file_content = req.POST['message'].encode()
            filename = 'text_message.txt'
            filetype = 'text'
        
        if algorithm == "aes":
            randomkey = str(random.randint(100000, 999999))
            secret_key = randomkey.encode()
            
            # Encrypt data
            aesencrypted_data = encrypt(file_content, secret_key)
            enc_path = os.path.join("static/AES/encryptedfiles/", f"enc_{filename}")
            with open(enc_path, 'wb') as file:
                file.write(aesencrypted_data)
                
            # Decrypt data for verification
            aesdecrypted_data = decrypt(aesencrypted_data, secret_key)
            dec_path = os.path.join("static/AES/files/", f"dec_{filename}")
            with open(dec_path, 'wb') as file:
                file.write(aesdecrypted_data)
                
            encrypt_text = Encryptedmodel(
                useremail=req.session['useremail'],
                textcontent=aesencrypted_data.decode('utf-8', errors='ignore')[:100],  # Store first 100 chars
                filekey=secret_key.decode(),
                encfilepath=enc_path,
                decfilepath=dec_path,
                filename=filename,
                filetype=filetype
            )
            encrypt_text.save()
            
        elif algorithm == "ecc":
            randomkey = str(random.randint(100000, 999999))
            secret_key = randomkey.encode()
            
            # Encrypt a message using the Fernet cipher
            encrypted_message = fernet_key.encrypt(file_content)
            decrypted_message = fernet_key.decrypt(encrypted_message)
            
            enc_path = os.path.join("static/ECC/encryptedfiles/", f"enc_{filename}")
            with open(enc_path, 'wb') as file:
                file.write(encrypted_message)
                
            dec_path = os.path.join("static/ECC/files/", f"dec_{filename}")
            with open(dec_path, 'wb') as file:
                file.write(decrypted_message)
                
            encrypt_text = Encryptedmodel(
                useremail=req.session['useremail'],
                textcontent=encrypted_message.decode('utf-8', errors='ignore')[:100],  # Store first 100 chars
                filekey=secret_key.decode(),
                encfilepath=enc_path,
                decfilepath=dec_path,
                filename=filename,
                filetype=filetype
            )
            encrypt_text.save()
            
            messages.success(req, f"{filename} encrypted successfully! Decryption Key: {secret_key.decode()}")
        return render(req, ENCRYPTDATAPAGE)
    return render(req, ENCRYPTDATAPAGE)

def viewfiles(req):
    if 'useremail' not in req.session:
        return redirect('login')
    encrypted_data = Encryptedmodel.objects.filter(useremail=req.session['useremail'])

    if encrypted_data:
        return render(req, VIEWFILESPAGE, {'encrypted_data': encrypted_data, 'file': 'yesfile'})
    else:
        email = req.session['useremail']
        return render(req, VIEWFILESPAGE, {'encrypted_data': encrypted_data, 'file': 'nofile', 'email': email})

def decryptdata(req):
    if 'useremail' not in req.session:
        return redirect('login')
    data = Filerequestmodel.objects.filter(status='approved', receiveremail=req.session['useremail'])
    encrypted_data = Encryptedmodel.objects.all()  # Get all encrypted files to match with requests
    return render(req, DECRYPTPAGE, {"filedata": data, "encrypted_data": encrypted_data})

def viewmyfiles(req, id):
    if req.method == "POST":
        filekey = req.POST.get('filekey')
        
        try:
            # Verify key
            file_record = Encryptedmodel.objects.get(id=id, filekey=filekey)
            dec_path = file_record.decfilepath
            filename = file_record.filename
            
            with open(dec_path, "rb") as f:
                file_content = f.read()
                
            # For text files, display content; for binary files, provide download
            if file_record.filetype == 'text' or filename.endswith(('.txt', '.md', '.py', '.js', '.html', '.css')):
                try:
                    content = file_content.decode('utf-8')
                    return render(req, VIEWMYFILESPAGE, {'id': id, 'files': 'False', 'content': content, 'filename': filename, 'is_text': True})
                except UnicodeDecodeError:
                    # Binary file, provide download link
                    return render(req, VIEWMYFILESPAGE, {'id': id, 'files': 'False', 'content': None, 'filename': filename, 'is_text': False, 'file_url': f'/static/{dec_path.replace("static/", "")}'})
            else:
                # Binary file
                return render(req, VIEWMYFILESPAGE, {'id': id, 'files': 'False', 'content': None, 'filename': filename, 'is_text': False, 'file_url': f'/static/{dec_path.replace("static/", "")}'})
                
        except Encryptedmodel.DoesNotExist:
            messages.warning(req, "Key is not valid...!")
            return render(req, VIEWMYFILESPAGE, {'id': id, 'files': 'True'})
            
    return render(req, VIEWMYFILESPAGE, {'id': id, 'files': 'True'})

def sendrequest(req, id):
    if 'useremail' not in req.session:
        return redirect('login')
    if req.method == 'POST':
        receiver_email = req.POST.get('receiver_email')
        if not receiver_email:
            messages.error(req, 'Please enter a recipient email.')
            return redirect('viewfiles')

        # Validate that receiver exists and is activated
        try:
            receiver = userreg.objects.get(email=receiver_email, status='Activated')
        except userreg.DoesNotExist:
            messages.error(req, 'Recipient email not found or account not activated.')
            return redirect('viewfiles')

        # Check if user is not trying to share with themselves
        if receiver_email == req.session.get('useremail'):
            messages.error(req, 'You cannot share files with yourself.')
            return redirect('viewfiles')

        data = Encryptedmodel.objects.get(id=id)
        filerequest = Filerequestmodel(
            fileid=data.id,
            useremail=data.useremail,
            textcontent=data.textcontent,
            filekey=data.filekey,
            receiveremail=receiver_email
        )
        filerequest.save()
        messages.success(req, f'File shared with {receiver.name} ({receiver_email}).')
        return redirect('viewfiles')

    return redirect('viewfiles')

def filerequest(req):
    if 'useremail' not in req.session:
        return redirect('login')
    data = Filerequestmodel.objects.filter(useremail=req.session['useremail'], status='pending')
    encrypted_data = Encryptedmodel.objects.all()  # Get all encrypted files to match with requests
    return render(req, FILEREQUESTPAGE, {'filedata': data, 'encrypted_data': encrypted_data})

def sendkey(req, fileid):
    if 'useremail' not in req.session:
        return redirect('login')
    try:
        dc = Filerequestmodel.objects.get(fileid=fileid, useremail=req.session['useremail'], status='pending')
        
        subject = "No reply - Decryption Key"
        cont = "Here is the private key to decrypt the file."
        key = dc.filekey
        m1 = "This message is automatically generated, so please do not reply to this email."
        m2 = "Thank you,"
        m3 = "Regards,"
        m4 = "Cloud Service Provider."
        
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [dc.receiveremail]
        text = f"{cont}\n{key}\n{m1}\n{m2}\n{m3}\n{m4}"
        
        send_mail(subject, text, email_from, recipient_list, fail_silently=False)
        
        dc.status = 'approved'
        dc.save()
        messages.success(req, f'File request approved! The decryption key {key} was sent to the user.')
    except Exception as e:
        print(f"Error sending email: {e}")
        messages.success(req, f'File request approved manually (Email error). The decryption key is {key}.')
        dc.status = 'approved'
        dc.save()
        
    return redirect("filerequest")


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('index')


def filetransactions(request):
    if 'useremail' not in request.session:
        return redirect('login')
    
    user_email = request.session['useremail']
    
    sent_requests = Filerequestmodel.objects.filter(useremail=user_email)
    received_requests = Filerequestmodel.objects.filter(receiveremail=user_email)
    encrypted_files = Encryptedmodel.objects.all()
    
    transactions = []
    
    for req in sent_requests:
        file = next((f for f in encrypted_files if str(f.id) == str(req.fileid)), None)
        transactions.append({
            'type': 'sent',
            'other_user': req.receiveremail,
            'filename': file.filename if file else 'Unknown',
            'status': req.status,
            'datetime': req.datetime,
            'fileid': req.fileid
        })
        
    for req in received_requests:
        file = next((f for f in encrypted_files if str(f.id) == str(req.fileid)), None)
        transactions.append({
            'type': 'received',
            'other_user': req.useremail,
            'filename': file.filename if file else 'Unknown',
            'status': req.status,
            'datetime': req.datetime,
            'fileid': req.fileid
        })
        
    # Sort chronologically
    transactions.sort(key=lambda x: x['datetime'] if x['datetime'] else timezone.now())
    
    # Group by other_user
    grouped_transactions = {}
    for t in transactions:
        user = t['other_user']
        if user not in grouped_transactions:
            grouped_transactions[user] = []
        grouped_transactions[user].append(t)
        
    context = {
        'grouped_transactions': grouped_transactions,
    }
    
    return render(request, 'filetransactions.html', context)


def download_encrypted_file(request, file_id):
    """Download encrypted file"""
    if 'useremail' not in request.session:
        return redirect('login')
    
    try:
        file_record = Encryptedmodel.objects.get(id=file_id, useremail=request.session['useremail'])
        file_path = file_record.encfilepath
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            response = HttpResponse(file_data, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="encrypted_{file_record.filename}"'
            return response
        else:
            raise Http404("File not found")
    except Encryptedmodel.DoesNotExist:
        raise Http404("File not found")
