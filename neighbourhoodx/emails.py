from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_welcome_email(name,receiver):
    # subject and sender
    subject = 'Administrator Registration Successful'
    sender = 'renderwes@gmail.com'

    text_content = render_to_string('email/txt_admin.txt',{"name": name})
    html_content = render_to_string('email/txt_admin.html',{"name": name})

    msg = EmailMultiAlternatives(subject ,text_content,sender,[receiver])
    msg.attach_alternative(html_content,'text/html')
    msg.send()


def send_welcome_resident(name,username,password,administrator,neighbourhood,receiver):
    # subject and sender
    subject = 'Welcome to Neighbourhood X'
    sender = 'renderwes@gmail.com'

    text_content = render_to_string('email/txt_resident.txt',{"name": name, "username":username, "password":password, "administrator":administrator, "neighbourhood":neighbourhood})
    html_content = render_to_string('email/txt_resident.html',{"name": name, "username":username, "password":password, "administrator":administrator, "hood":neighbourhood})

    msg = EmailMultiAlternatives(subject,text_content,sender,[receiver])
    msg.attach_alternative(html_content,'text/html')
    msg.send()