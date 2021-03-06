def send_email(emailqueue):
  from django.core.mail import send_mail
  from django.template import Context, Template

  body = Template(emailqueue.email.body)
  subject = Template(emailqueue.email.subject)
  group = emailqueue.email.group
  subscriber = emailqueue.subscriber
  gs = subscriber.groupsubscriber_set.get(group=group)
  data = {
    "subscriber": subscriber,
    "group": group,
    "gs": gs
  }

  body = body.render(Context(data))
  subject = subject.render(Context(data))

  try:
    send_mail(subject, body, "%s <%s>" % (group.from_name, group.from_email), [subscriber.email], fail_silently=False)
    emailqueue.sent = True
    emailqueue.save()
    return True
  except:
    from datetime import datetime, timedelta
    day = timedelta(days=1)
    emailqueue.send_date = datetime.now() + day
    emailqueue.save()
    return False


def create_confirmation_email(group):
  from list.models import Email
  confirmation_template = None
  try:
    confirmation_template = Email.objects.get(name__startswith="confirmation", group=group)
  except:
    confirmation_template = Email(name="confirmation_%s" % (group.name),
                                  group = group,
                                  subject = "Confirm your subscription",
                                  body =
"""Hey {{subscriber.first_name}}!

Please confirm your subscription to {{group.name}} list!

Click here to confirm:
https://mailinglist.herokuapp.com/confirm/{{gs.activation_key}}

Thanks!

-- Chris
""",
                                  days=0)
    confirmation_template.save()
  return confirmation_template

def queue_confirmation_email(user, group, activation_key):
  from list.models import EmailQueue
  # add email in email queue move to the top of the queue
  email = EmailQueue(subscriber=user, email=create_confirmation_email(group))
  email.save()

  # send confirmation email
  send_email(email)
