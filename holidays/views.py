from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django import forms 

from holidays import sieve

from django.forms.util import ErrorList

class SimpleErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return u''
        return u'%s' % ''.join([u'%s' % e for e in self])

class MailForm(forms.Form):
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    subject.widget.attrs = {'class': 'form-control'}
    message.widget.attrs = {'class': 'form-control'}

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email.widget.attrs = {'class': 'form-control'}
    username.widget.attrs = {'class': 'form-control'}
    password.widget.attrs = {'class': 'form-control'}
    
def index(request):
    e = ""
    if request.method == 'POST': 
        login = LoginForm(request.POST, error_class=SimpleErrorList)
        if login.is_valid(): # All validation rules pass     
            request.session['email'] = login.cleaned_data['email']
            request.session['username'] = login.cleaned_data['username']  
            request.session['password'] = login.cleaned_data['password']  

            try: 
                s = sieve.sieve("bornite.isotoma.com")
                s.authenticate(request.session['username'], request.session['password'])
            except sieve.SieveError, e:
                print e
                return render (request, 'holidays/index.html', {
                    'login' : login,
                    'error_message' : e
                })
            request.session['authenticated'] = True
            return HttpResponseRedirect('message.html') 
            
    else:
        login = LoginForm() 

    return render(request, 'holidays/index.html', {
        'login': login,
    })
            
def message(request):
    try:
        request.session['authenticated']
    except Exception: 
        return HttpResponseRedirect('/holidays/') 
      
    s = sieve.sieve("bornite.isotoma.com")
    s.authenticate(request.session['username'], request.session['password'])
    email_address = request.session['email']
    active_status = s.get_active()

    # delete the default ingo script if it exists
    if active_status == "ingo":
        s.desactivate()
        active_status = s.get_active() 
    
    if  request.method == 'POST':   
        mail = MailForm(request.POST, error_class=SimpleErrorList)
        if 'set_away_message' in request.POST:        
            if mail.is_valid():
                message = mail.cleaned_data['message']
                subject = mail.cleaned_data['subject']
                
                awaymessage = """
                # Set by gwildaynotifr
                require "vacation";
                if allof ( not exists ["list-help", "list-unsubscribe", "list-subscribe", "list-owner", "list-post", "list-archive", "list-id", "Mailing-List"], not header :comparator "i;ascii-casemap" :is "Precedence" ["list", "bulk", "junk"], not header :comparator "i;ascii-casemap" :matches "To" "Multiple recipients of*" ) {
                vacation :days 14 :addresses ["{email}"] :subject "{line}"
                "{contents}
                ";
                redirect "{email}";
                keep;
                }
                """.format(contents = message, line = subject, email = email_address)        
                s.putscript('holidaymessage', awaymessage)
                # activate it
                s.activate('holidaymessage')
                # get active script -> tortuegenial
                print s.get_active()   
                active_status = s.get_active()      
                return render(request, 'holidays/message.html', {
                    'message_active': active_status,
                    'mail': mail
                })
        elif 'deactivate' in request.POST:
            if s.get_active:
                s.desactivate()
                active_status = s.get_active() 
                print "deactivate"
            return render(request, 'holidays/message.html', {
                'message_active': active_status,
                'mail': mail
            })
    else:
        mail = MailForm()
    return render(request, 'holidays/message.html', {
        'message_active': active_status,
        'mail': mail
    })
        
    




