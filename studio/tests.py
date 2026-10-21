from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase,Client,override_settings
from django.urls import reverse
from .models import Project,Asset

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class StudioFlowTests(TestCase):
 def test_verified_private_sketch_flow(self):
  c=Client()
  r=c.post('/signup/',{'username':'designer','email':'DESIGNER@example.com','password1':'StrongPassword238!','password2':'StrongPassword238!'})
  self.assertEqual(r.status_code,200)
  u=User.objects.get(username='designer');self.assertFalse(u.is_active)
  self.assertFalse(c.login(username='designer',password='StrongPassword238!'))
  self.assertEqual(u.email,'designer@example.com')
  import re
  link=re.search(r'http://[^\s]+',mail.outbox[0].body).group()
  self.assertEqual(c.get(link).status_code,302)
  self.assertEqual(c.get(link).status_code,200) # one-time activation, no second login
  login_response=c.post('/login/',{'username':'designer','password':'StrongPassword238!'})
  self.assertEqual(login_response.status_code,302)
  self.assertEqual(login_response.url,'/login/code/')
  self.assertEqual(c.get('/projects/').status_code,302)
  code=re.search(r'\b[0-9]{6}\b',mail.outbox[-1].body).group()
  self.assertEqual(c.post('/login/code/confirm/',{'code':code}).status_code,302)
  r=c.post('/projects/new/',{'title':'Courtyard house','description':'First study'})
  p=Project.objects.get(title='Courtyard house');self.assertEqual(r.status_code,302)
  bad=SimpleUploadedFile('evil.html',b'<script>x</script>',content_type='image/png')
  c.post(reverse('upload',args=[p.pk]),{'image':bad})
  self.assertEqual(Asset.objects.count(),0)
  b=BytesIO();Image.new('RGB',(80,80),'red').save(b,'PNG')
  good=SimpleUploadedFile('../drawing.png',b.getvalue(),content_type='image/png')
  c.post(reverse('upload',args=[p.pk]),{'image':good})
  a=Asset.objects.get(kind='reference')
  self.assertEqual(c.get(reverse('image',args=[a.pk])).status_code,200)
  c.post(reverse('sketch',args=[a.pk]))
  self.assertEqual(Asset.objects.filter(kind='sketch').count(),1)
  other=User.objects.create_user('other',password='DifferentPassword238!');c.force_login(other)
  self.assertEqual(c.get(reverse('project',args=[p.pk])).status_code,404)
  self.assertEqual(c.get(reverse('image',args=[a.pk])).status_code,404)
  self.assertEqual(c.post(reverse('sketch',args=[a.pk])).status_code,404)
  self.assertEqual(c.post(reverse('upload',args=[p.pk])).status_code,404)
 def test_login_limiter(self):
  c=Client()
  for _ in range(5):c.post('/login/',{'username':'nobody','password':'wrong'})
  self.assertEqual(c.post('/login/',{'username':'nobody','password':'wrong'}).status_code,429)
