import io,uuid,secrets,hashlib,hmac,time
from PIL import Image,ImageOps,ImageFilter,ImageFile,UnidentifiedImageError
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from django.db import transaction
from django.http import FileResponse,Http404
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import SignupForm,ProjectForm
from .models import Project,Asset
Image.MAX_IMAGE_PIXELS=18_000_000
ImageFile.LOAD_TRUNCATED_IMAGES=False
signer=TimestampSigner(salt='studio-email-verification-v1')

def home(request):return render(request,'studio/home.html')
def signup(request):
 if request.user.is_authenticated:return redirect('projects')
 form=SignupForm(request.POST or None)
 if request.method=='POST' and form.is_valid():
  with transaction.atomic():
   user=form.save(commit=False);user.email=form.cleaned_data['email'];user.is_active=False;user.save()
   url=request.build_absolute_uri(reverse('verify',args=[signer.sign(str(user.pk))]))
   send_mail('Verify your BuildAI email',f'Open this link within 24 hours to verify your account:\n{url}',settings.DEFAULT_FROM_EMAIL,[user.email])
  return render(request,'studio/check_email.html')
 return render(request,'studio/form.html',{'form':form,'title':'Create account','button':'Create account'})
def verify(request,token):
 try:pk=int(signer.unsign(token,max_age=86400))
 except (BadSignature,SignatureExpired,ValueError):return render(request,'studio/message.html',{'title':'Link invalid','message':'Your link is invalid or expired. Contact the administrator to resend verification.'},status=400)
 user=get_object_or_404(User,pk=pk)
 if user.is_active:return render(request,'studio/message.html',{'title':'Already verified','message':'Your account is verified. Sign in to continue.'})
 user.is_active=True;user.save(update_fields=['is_active'])
 messages.success(request,'Email verified. Sign in to continue.')
 return redirect('login')
@login_required
def projects(request):return render(request,'studio/projects.html',{'rows':Project.objects.filter(owner=request.user).order_by('-updated_at')})
@login_required
def new_project(request):
 form=ProjectForm(request.POST or None)
 if request.method=='POST' and form.is_valid():
  p=form.save(commit=False);p.owner=request.user;p.save();return redirect('project',pk=p.pk)
 return render(request,'studio/form.html',{'form':form,'title':'New project','button':'Create project'})
@login_required
def project(request,pk):
 p=get_object_or_404(Project,pk=pk,owner=request.user)
 return render(request,'studio/project.html',{'project':p,'assets':p.assets.order_by('-created_at')})
@login_required
@require_POST
def archive(request,pk):
 p=get_object_or_404(Project,pk=pk,owner=request.user);p.archived=not p.archived;p.save(update_fields=['archived','updated_at']);return redirect('project',pk=pk)
def private_path(key):return settings.PRIVATE_STORAGE/key[:2]/key
@login_required
@require_POST
def upload(request,pk):
 p=get_object_or_404(Project,pk=pk,owner=request.user,archived=False)
 f=request.FILES.get('image')
 if not f or f.size>8*1024*1024:
  messages.error(request,'Choose an image smaller than 8 MB.');return redirect('project',pk=pk)
 try:
  data=f.read(8*1024*1024+1)
  if len(data)>8*1024*1024:raise ValueError
  im=Image.open(io.BytesIO(data));im.verify()
  im=Image.open(io.BytesIO(data))
  if im.format not in ('JPEG','PNG','WEBP') or im.width*im.height>18_000_000:raise ValueError
  im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((3000,3000))
  key=f'{uuid.uuid4().hex}.jpg';path=private_path(key);path.parent.mkdir(parents=True,exist_ok=True)
  im.save(path,format='JPEG',quality=88,optimize=True)
  try:Asset.objects.create(project=p,kind='reference',file_key=key)
  except Exception:path.unlink(missing_ok=True);raise
  messages.success(request,'Reference image uploaded privately.')
 except (ValueError,UnidentifiedImageError,Image.DecompressionBombError,OSError):messages.error(request,'Invalid or oversized image. Use JPEG, PNG or WebP.')
 return redirect('project',pk=pk)
@login_required
def image(request,asset_id):
 a=get_object_or_404(Asset,pk=asset_id,project__owner=request.user)
 try:return FileResponse(open(private_path(a.file_key),'rb'),content_type='image/jpeg',headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'})
 except FileNotFoundError:raise Http404
@login_required
@require_POST
def sketch(request,asset_id):
 a=get_object_or_404(Asset,pk=asset_id,project__owner=request.user,project__archived=False,kind='reference')
 with Image.open(private_path(a.file_key)) as source:
  gray=ImageOps.grayscale(source)
  edges=ImageOps.invert(gray.filter(ImageFilter.FIND_EDGES))
  # Deterministic pencil-style filter; not generative AI.
  out=ImageOps.autocontrast(Image.blend(gray,edges,0.75))
  key=f'{uuid.uuid4().hex}.jpg';path=private_path(key);path.parent.mkdir(parents=True,exist_ok=True);out.convert('RGB').save(path,'JPEG',quality=88)
 try:Asset.objects.create(project=a.project,kind='sketch',source=a,file_key=key)
 except Exception:path.unlink(missing_ok=True);raise
 messages.success(request,'Concept sketch created from the reference image.')
 return redirect('project',pk=a.project_id)

class LimitedLoginView(LoginView):
 template_name='studio/login.html'
 def dispatch(self,request,*args,**kwargs):
  if request.method=='POST':
   import hashlib
   raw=(request.META.get('REMOTE_ADDR','')+'|'+request.POST.get('username','').lower()).encode()
   self.limit_key='login:'+hashlib.sha256(raw).hexdigest()
   if cache.get(self.limit_key,0)>=5:return HttpResponse('Too many attempts. Try again in 15 minutes.',status=429)
  return super().dispatch(request,*args,**kwargs)
 def form_invalid(self,form):
  count=cache.get(self.limit_key,0);cache.set(self.limit_key,count+1,900)
  return super().form_invalid(form)
 def form_valid(self,form):
  cache.delete(self.limit_key)
  user=form.get_user()
  code=f'{secrets.randbelow(1_000_000):06d}'
  digest=hmac.new(settings.SECRET_KEY.encode(),code.encode(),hashlib.sha256).hexdigest()
  self.request.session['pending_login']={'uid':user.pk,'digest':digest,'until':int(time.time())+600,'attempts':0}
  send_mail('Your BuildAI sign-in code',f'Your sign-in code is {code}. It expires in 10 minutes.',settings.DEFAULT_FROM_EMAIL,[user.email])
  return redirect('login_code')

@require_POST
def confirm_login_code(request):
 pending=request.session.get('pending_login')
 if not pending or pending['until']<time.time() or pending['attempts']>=5:
  request.session.pop('pending_login',None)
  return render(request,'studio/message.html',{'title':'Code expired','message':'Please sign in again.'},status=400)
 code=request.POST.get('code','')
 digest=hmac.new(settings.SECRET_KEY.encode(),code.encode(),hashlib.sha256).hexdigest()
 if not (len(code)==6 and code.isdigit() and hmac.compare_digest(digest,pending['digest'])):
  pending['attempts']+=1;request.session['pending_login']=pending
  messages.error(request,'Incorrect code.')
  return redirect('login_code')
 user=get_object_or_404(User,pk=pending['uid'],is_active=True)
 request.session.pop('pending_login',None)
 login(request,user)
 return redirect('projects')

def login_code(request):
 if not request.session.get('pending_login'):return redirect('login')
 return render(request,'studio/code.html')

