# Use simplelogin.io's API to batch create reverse aliases (i.e. contacts) for one of your aliases

# Why do I need this?
Right now you can only use the UI to create a contact one at a time so if you
want to send an email for the first time to a bunch of people, that comes out
of one of you simplelogin.io aliases, you need to do the following:
1. go into the aliases home
2. find your alias, click details
3. click contacts
4. put the email address you want to contact from your alias
5. then you'll get a reverse-alias that you can copy and paste into your
   alias' mailbox to send an email that will appear as if it came out of your
   alias

*Ain't no way I am doing this for more than 5 emails... Too lazy*

# Isn't there a better way?
Yeah. For instance, if Simplelogin.io allows SMTP forwarding directly. Then
some email services, like Gmail, will allow you send emails from any of your
aliases without this reverse-alias gobblygook.

This is not a feature yet, and it is liked in the simplelogin.io roadmap.
I found one on trello, but not sure if that's the official one.

# How do I use this code then. Fine, I get it, no better option yet.
Just run it.

First make sure you go to your simplelogin.io, login, and on the top right
corner you'll see a dropdown that shows you your API Keys. Create one, and put
it in a .env file on the root of this project. It should look like this:

.env
```
SIMPLELOGIN_APIKEY=<whatever you got when you created it in simplelogin.io>
```

```shell
pip install -r requirements.txt
python batch_create_contacts.py <somealiasIvegot@somedomain.com> <a path to
a csv with a "contact" column that has all the emails you want a contact for>
```

