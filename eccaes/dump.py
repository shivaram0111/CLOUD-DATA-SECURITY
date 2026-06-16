import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eccaes.settings')
django.setup()
from myapp.models import userreg
with open('debug_users.txt', 'w') as f:
    for u in userreg.objects.all():
        f.write(f"{u.id} | {u.email} | {u.name} | {u.contact} | {u.address}\n")
