# WHENEVER YOU WANT TO START THE VIRTUAL DEV: source ~/.virtualenvs/caps/bin/activate

This project doesn't really require a readme (yet), but I'm just keeping this to track progress and see what I need to do...

One thing I should focus on is working outside in.

This might come in handy for providing back links: <a href="javascript:history.go(-1)">back</a>

# TODO:
* see image issue
* ## Network / Nonprofits
	* maybe a success message on creation/update? | https://docs.djangoproject.com/en/3.0/ref/contrib/messages/#adding-messages-in-class-based-views
	* soft deleting as an option (a moderator could recover a deleted object up to 2 weeks later or so) | https://medium.com/@adriennedomingus/soft-deletion-in-django-e4882581c340 | this one is probably better: https://blog.khophi.co/soft-delete-django-quickly/
	* ### Forms
		* markdown for the volunteer description would be pretty cool, I think
		* when you refresh the page, all of the field values are kept. However, the address is NOT.

* ## User system / user classess

	* create groups | https://docs.djangoproject.com/en/3.0/ref/contrib/auth/#django.contrib.auth.models.Group
	* if you're a moderator or nonprofit representative, this'll show up on your user profile
	* ### Reporting System
		* If a nonprofit is flagged true, then send an email with the reason | https://docs.djangoproject.com/en/3.0/topics/email/#send-mass-mail
			* scratch that... first, add a many to many field of reasons, similar to tags, to nonprofits and networks. Then, if they have a reason, it will automatically pop up as flagged in the template view.
		* reports should probably be a separate model that has a many to many relationship with nonprofits and networks, and could be assigned or deleted
		* when a user gets their own account reported, they see a warning message in the top of their profile, and their background image in the navbar turns red | https://docs.djangoproject.com/en/3.0/ref/contrib/messages/#expiration-of-messages
* ## Calendar
	* fix rrule events
	* add some way to have a created_by attribute to events. If you created a network event, or if you are a nonprofit rep, or if it's your personal user event that you created, then add "editable" in fullcalendar
	* since I have sign up events, I'll have to somehow adjust the repeating thing, because you could sign up on one week, but the next week, you would be still be signed up which is bad. Or, easy route, sign ups are incompatable with repeating events!
	* Users can 'subscribe' to network calendars and nonprofit calendars, adding all of these events to their calendar. They can also just add specific events to their cals
	* In the javascript for the event update/create, I'm going to have to override some things; the calendar will be determined by an html created dropdown that has the values for the other nonprofits in the network, and their own user calendar. When this dropdown value changes, it automatically redirects them to the respective createview/update view of that calendar.
	* create views and forms
		* events and calendars will all have crud views. Events will have detail views.
		* Finish adding sign-ups to Events. Users can sign up (many users can sign up to one calendar event, so like a reverse fk), but you can also sign up without an account, you just leave your name and email. Furthermore, sign-up event creators can add
	
	* import events from a google cal
	* rss feeds
	* it's called calendar, but do I even want to show a calendar screen? Could it be like this?: https://www.kpcw.org/community-calendar#stream/0

* ##Organizations
	* Organizations are a way for groups of users to connect to specific nonprofits and networks
	* Organizations need to have their own calendars, so their own calendar views and urls in cal.urls.py, and their own model in cal.models.py, and probably some stuff in the admin site, too
* ## Later:
	* 404 error page isn't getting css.
	* When making the site look good, I'll probably have to override all of the forms with custom elements. See nonprofit_map and change all of that dom element creation stuff that I did.
	* make more favicons (for phones) and more meta data (twitter card, etc)
	* write some general tests
	* ordering networks/nonprofits based on distance to you: https://geopy.readthedocs.io/en/stable/#module-geopy.distance
	* switch image uploading to a service like aws
	* use regex on phone model to enforce an answer
	* add a button you can use to get directions to a nonprofit on its detail view
	* set keywords and author meta for base.html

# Issues
* if you refresh a network when you're creating it, the coords will reset while the title stays, which isn't good. I should clear the forms on page reload for this view.
* whenever you add a nonprofit with the same name in the same network, it rightfully raises an error, but not in the form view which is what I want
* issue: networks, "Lisbon, Peru" and "Lisbon Peru" can be created because they have technically different titles (comma vs no comma), but they have the same slug
* potential issue: image gets resized every time it is saved if it's above a certain width. While I set this to 100% conversion, I'm curious if future loss occurs
	* to solve this, wrap the whole thing in an if image width > 1024 px, just to be safe and eficient
* original big image doesn't get delted after resizing happens

# What was done
* 12/30 added tests, static files, tagging, the flagged attribute to both network and nonprofit, and changed the admin site
* 12/31 added views for adding a network and looked into forms
* 1/1 added the network change, update, and delete forms + views / urls
* 1/4 WOO! Checkboxes for tags, now you can get coordinates for networks just by adding them, etc.
* 1/7 two network forms for createview and updateview now, nonprofit forms are coming along. Found more issues
* 1/12 detail network view now uses an actual generic detail view, found and fixed a slug error (slugs are now unique with the scope of the individual network), and now nonprofit detail views and delete views kind of work... now reverses back to detail view after updating
* 1/16 nonprofit delete view and detail view now work even if name is duplicated, found and fixed other non detail view bug, changed view success redirects, fixed tags not showing up, and switched to github.
* 1/18 - 1/19 asked a fire stackoverflow questions, coords now need address to generate and have to be None type previously, changed geocoder to MapBox, foreign key is automatically created when you add a nonprofit, update form differs from create form for nonprofit (prescence of network field), added image uploads, and automatic image resizing. Only src_link or src_file can be filled, not both. Required at least one of 4 nonprofit forms to filled out and worked with mapbox in the network create view.
* 1/20 I removed the network geocoding funcition in the forms and replaced it with a more intuitive, map function, instead. Coorindates are now generated with a mapbox map for network update and create view
* 1/21 added a flyTo for the network map to make it more similar to the nonprofit geocoder movement, changed the marker style to something more unique, used network data in nonprofit create/update to bbox geocoding, moved all of the template views into better folders, worked on base.html and extending it
* 1/25 show and hide map/coordinates in nonprofit create/update view if no coordinates, clear coords on submit if there's no address, sets default coords to network coords if they don't exist, moved map and geocoder and coordinates by where the address field is, and completely automated the coordinates and address field! Added a custom template filter to use regex to shorten addressess that are too long.
* 1/26 added a map for the detail view of the network and nonprofit, and added scss, a navbar, and a gravitar. Moved around some templates. You can now log in and out, and reset your password if you forgit it. I added login restrictions to some views. I added a custom user model, too.
* 1/28 renamed the customuser model (which took a lot of trouble), and created a user profile screen
* 1/29 changed the navbar up just a bit, added the users' created nonprofits/networks to their profile, added a redirect view. If you're already logged in, it fills out your email for the password reset form. I overrided the password reset email, too, and its subject. I realized that before I add groups, I should finish with adding the calendar app as well as the reporting system
* 1/30 Added a favicon. Added an /accounts/profile view that shows you're account if you're logged in, prompts for log in otherwise. Changed the default main page (/) to reflect whether you're logged in or not. The navbar now has an 'add a nonprofit' button if you're on a network detail page. You can only delete networks and nonprofits that you've either created, or if you explicitly have the permission 'delete_network' or 'delete_nonprofit'. Overrided the 403 forbidden error. Custom 404 error, too, but for some reason that doesn't get css.
* 1/31 If you're already logged in, you can't sign up or log in again, you get redirected to main, and a message appears and tells you that you can't do that. Put an indicator on the navbar if you're on a certain page. Put password requirements on login page. Users can delete their own account, or an admin can delete users' accounts. Replaced permission denied with a redirect and message.
* 2/4 Most of my work was troubleshooting a virtualenv, so few changes here. Added the event model, a recurrence field (after a lot of research), and some values for it. TODO is to add more model forms for calendar and event, as well as basic views (CRUD). An event belongs to a calendar, and a calendar belongs to either a nonprofit, network, or user.
* 2/5 Added some calendar views to redirect to where they would naturally be (calendars/<network>/<nonprofit> redirects to the network/<network>/<nonprofit>#calendar, where the calendar would be). Did some more form and model work. In the admin site, added a way to add calendars to pre-existing things. Added calendar to network detail view under #calendar.
* 2/6 Calendars can now have a fk relationship to themselves and are one-to-one with network, user, nonprofit. Nonprofit calendars are auto created. Network calendars are auto created. Added a custom calendar filter on the admin page. User calendars are auto created. On the event form, changed some of the all day stuff. The power went out so I wasn't able to commit.
* 2/8 Added some more event fields. Set the calendar attribute to be manytomany so that you can add it to multiple calendars (user calendars, etc). Developed the event form more. Account anniversary gets created every time a user signs up. Added fullcalendar scripts and stuff. Added an event add view, but it looks weird, and I probably won't use it. Added events to calendar. I got rrule to work, but depending on what I do in the add event view, I might have to change some stuff. Maybe I won't even have to use the schedule package at all, just create rrules on the fly with rrule.js? Also, I have to make sure I get the duration right, because right now, it's just auto two hours.