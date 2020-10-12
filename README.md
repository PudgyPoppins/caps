# WHENEVER YOU WANT TO START THE VIRTUAL DEV: source ~/.virtualenvs/caps/bin/activate
# source env/bin/activate

This project doesn't really require a readme (yet), but I'm just keeping this to track progress and see what I need to do...

One thing I should focus on is working outside in.

This might come in handy for providing back links: <a href="javascript:history.go(-1)">back</a>

# TODO:
* see image issue
* ## Network / Nonprofits
	* add announcements (TextPost model in organization) to nonprofits so that they can make them.
		* only nonprofit representatives can create announcements
	* add a way to do nonprofit representatives, with a proof / application system
	* maybe a success message on creation/update? | https://docs.djangoproject.com/en/3.0/ref/contrib/messages/#adding-messages-in-class-based-views
	* soft deleting as an option (a moderator could recover a deleted object up to 2 weeks later or so) | https://medium.com/@adriennedomingus/soft-deletion-in-django-e4882581c340 | this one is probably better: https://blog.khophi.co/soft-delete-django-quickly/
	* ### Forms
		* markdown for the volunteer description would be pretty cool, I think
		* when you refresh the page, all of the field values are kept. However, the address is NOT.

* ## User system / user classess

	* create groups | https://docs.djangoproject.com/en/3.0/ref/contrib/auth/#django.contrib.auth.models.Group
	* if you're a moderator or nonprofit representative, this'll show up on your user profile
		* nonprofit representatives are attatched to a nonprofit in a model. However, I should still add them all to a group, so that way, I can get who they are, then set their home:main view to their nonprofit.
	* ### Reporting System
		* If a nonprofit is flagged true, then send an email with the reason | https://docs.djangoproject.com/en/3.0/topics/email/#send-mass-mail
			* scratch that... first, add a many to many field of reasons, similar to tags, to nonprofits and networks. Then, if they have a reason, it will automatically pop up as flagged in the template view.
		* reports should probably be a separate model that has a many to many relationship with nonprofits and networks, and could be assigned or deleted
		* when a user gets their own account reported, they see a warning message in the top of their profile, and their background image in the navbar turns red | https://docs.djangoproject.com/en/3.0/ref/contrib/messages/#expiration-of-messages
			* how about we send an email instead?
* ## Calendar
	* add a way to unsignup for events. Signed in users can only unsign-up themselves (or the nonprofit representative).
	* email users a day before their event?

	* updates for recurring:
		* this event: split the event, then update it
		* this and following events:
			* On the recurring event, change the RRULE; either add an UNTIL field with the date at that point, or modify the until (shortening it) to be at that point
			* Then, create a new recurring event with the same RRULE (save for the changed until value, and the changed dtstart), and apply the updates to it
			* do a filter search for children events that have a start_time after the original recurring event. For loop through 'em, apply the update, change the parent, then save
		* all events: 
			* apply the updates to the eldest event
			* search through all of the child events, and set all of the s_* field values as None, it'll inherit them from the eldest event!

	* important note: if an event is updated for "this and following events", then somebody goes back and edits "all events", then this just doesn't work.
		* the fix: modify code to allow parents to have multiple generations of children. We're going to have grandkids. Then, use some sort of recursive method to get all of the children of the original.

	* add a way to filter events shown on the calendar. Validity filtration is a must. Maybe also nonprofit filtration?
	* make a regex for an RRULE (and for that matter, a user-friendly field for the RRULE)

	* Users can 'subscribe' to network calendars and nonprofit calendars, adding all of these events to their calendar. They can also just add specific events to their cals
	
	* In the javascript for the event update/create, I'm going to have to override some things; the calendar will be determined by an html created dropdown that has the values for the other nonprofits in the network, and their own user calendar. When this dropdown value changes, it automatically redirects them to the respective createview/update view of that calendar.
		* I might not do this, actually
	* create views and forms
	
	* import events from a google cal | https://fullcalendar.io/docs/v3/google-calendar
	* rss feeds

* ##Organizations
	* goals and text posts
	* change the add link so that it sends an invite to the respective user, and they have to accept
	* orgs can pin nonprofits and networks to their page
	* add invite to moderator links?
	* add goals to user profiles when they get created, if they're in an organization

	* Organizations are a way for groups of users to connect to specific nonprofits and networks
		* Organizations can pin nonprofits or networks to their page
	* Organizations have leaderboards where they sort who has the most hours in their logging (verified plus verified and unverified scores)

* ##Logging
	* When a user signs up for an event, after the event has happened, then the nonprofit representative can verify that they helped out
	* Nonprofit representatives can also add a log for a user without an event
	* Users can add their own logs. They can select a nonprofit that's already added or write in their own. They can write in their hours, too.

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

# Brainstorming
* Handling exceptions:
	* Easiest way I can think of: When a user edits an event, there's a split. Another event gets created that doesn't have an rrule (one time), and is a child of the original. An exception day gets added to the original.

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
* 2/29 It's been a while! I removed the reccurrence package, if all it's doing is creating rrules, I might as well just do it myself.
* 3/2 Created a custom filter to get the duration for those recurring events. We're also back on the virtual dev, which will hopefully stay that way. Added a modal for events. Might do some more work with crispy forms in the future for form rendering.
* 3/7 Changed how the date was rendered on the modal.
* 3/28 Did a LOT of work adding organizations, and a bit of calendar stuff (which I have to complete).
* 4/9 Added the invitation model and started the create view. I need to see how I'll store dates for ALL of my stuff, including calendar. I installed moment.js so I can easily convert to different timezones. I'm not sure if I should store dates in American/Denver time (the default time for the server), or in UTC :shrug:
* 4/10 Invitations are now mostly added (create / join). I might next move on to requests (requesting to join an organization), or calendar subscriptions. Times are stored in UTC, and get converted on the fly. Middleware tries to detect user's timezone, but the user can override that in a form (home:set_timezone). Next, I should also show the timezone in all of the times from now on, and do utc time for forms like the event form where you enter the time in manually.
* 4/14 Allowed users to request to join, and mods/leaders can approve/deny this.
* 4/16 Added a copy to clipboard function for the invite links and fixed some validity issues. Added organizations to navbar. Made it so that remaining uses for join links show up instead of used uses. Added an update form for the user. Added the "display_name" field to the user forms. Added joined organizations to the user profile page. Made it so now leaders and moderators can add and kick members, and leaders can promote and demote users. Added update and delete views for the organization. I'll probably add the transfer ownership functionality next?
* 4/17 Added bulma, which may or may not stay. Fixed an error where users could still be added via a request or /add, even if they were already in the organization. Now, if users try to kick themselves they get sent to a leave link. Finished adding the leave functionality and transfer ownership functionality. If a user is the only member of an organization, and they leave, then the organization gets delete (no more members). Made it so that only mods/leaders of an organization can create invitation links. Invite links can only be created if they belong to a private organization. Got really close to getting a deleteview for invitations. 
* 4/18 Delete view for invitations works now. Added some more fields to organizations for contact information. No mapbox stuff for the address, tho. Added this information to the detail view. Added tokens to calendar events, and an ExcludedDates model. Now, events can be found with a unique token rather than a counted pk. Added a detail view for events. Events have a created_by attribute, and now, it's nonprofits that have a nonprofit_reps attribute. Made a total_attending integer field on event model so that non-signed in users can still sign up for events. Made a basic outline for the edit_event view, which still needs split functionality. Now don't allow the event_type 'Account Anniversary' on the EventForm. Fixed a problem where events weren't being added correctly. Added an rrule regex validator that doesn't really work to the model field for that. FINALLY added the JSON view for events, rather than cramming everything into one, unsecure script.
* 4/19 Pass a date to the event detail view, if it's an rrule event, with "d?=". Also verify that the date is part of the rrule, with a method that's now speedy fast! Added a way to return a success url for an event based on its calendar (model method), and used it on the event detail/update views.
* 7/12 I'm back. Added some git stuff and settings stuff for security. Made progress on the event sign_up. Altered some models to make things easier. Event sign up is completely done unless something horrible happens. It splits the event (if needed), it adds the excluded date, creates an attendee on the new event, etc. I should probably take a lot of the splitting stuff and getting the new event stuff and add it to a method, because what I plan on doing next is update the delete event view/edit event view to see if the user wants to update ALL of them or just the one. I also need to make sure these events show up / don't show up on the detail view properly.
* 8/7 I need more motivation :(. Anyways, put the date on the event detail view, made it easier to call model values (like event.title) with a property so I don't have to do a ton of if else statements to detect event children or not, successfully got exclusion dates working in the calendar, successfully got child events to show up in the calendar. Fixed a bug where an existing excluded date wouldn't let any events show up on that date.
* 8/7 I'm writing this again really just to test if ssh'ing is working. Here's another file change to test signing commits.
* 8/10 Made some more progress on deleting events. Fixed a bug where "None" descriptions were showing up. Fixed a problem where times weren't showing up correctly in the json file, then identified a new problem that arised from fixing that. Made a pretty hacky script to add times to the EXDATE thing. Got a real good plan down. Modified s_methods (like s_title) to be recursive to allow for multiple generations of events. Confirmed that UNTIL works in RRULE for fullcalendar, but that it has to go before any \nEXDATES's. Made it so that users can't sign up for a past event.
* 8/11 Added email field to attendee. Made seperate field for start_date and start_time, etc. Fixed everything to use new end_date and start_date stuff, but realized I probably could've gotten away with keeping just start_time. Fixed a problem with the calendar json (stupid commas). Deletion for non-rrule non-related events works. Completed single deletion (deletion_type=t) for all event types.
* 8/12 Deletion_type=a now works! Deletion for all types now works! Added permission check before deleting events.
* 8/13 update type a now works! Got really close on update type t, but ran into this big error. I managed to boil it down to the fact that running form.is_valid updates the connected event instance, which is not what I want when updating the child of an rrule, but confirming that the form is valid. Currently, this stops me from adding the excluded date, and then saving that part. Through sheer force of will I have, however, completely surpassed this issue using an incredibly hacky dictionary solution. update type t now works.
* 8/14 added EventFormUpdate, EventFormNetwork (different restrictions), and EventFormNetworkUpdate to the edit and update views. Streamlined the calendar_json.json file and fixed a problem where it didn't include second generation events. Completed the update_type = f, wich was a lot harder than expected. It also involved the use-case of setting the attendees to the new one, if applicable, which I didn't think about earlier, but was able to implement. Fixed an error with event.s_description not going past the second generation
* 8/20 My excuse for not working most everyday is that Arch Linux security is a rabbit hole with no end. I'm mature enough to quit that, now. I wrote a beast of an rrule regex, it could probably be more elegant, but if it works, it works.
* 8/22 Changed the forms to be more restrictive for creating new events. Started work on an rrule picker. I think I'm going to build my own, and I really think I can do it. Wrote out a plan of attack.
* 8/23 Changed a form value in Network. Got a bootstrap/jquery date picker in the event_form, which works pretty nicely. Spiced up some css.
* 8/24 Made some spicy checkbox buttons (toggleable, too, wow). Got really far in creating the rrule picker on the event form. Still have a bit more to go.
* 10/12 Calendar subscribe and unsubscribe now works entirely (or should work, at least). Also did some minor fixing up with calendar properties.

TODO: 
	* event create view
		* rrule selector
			* look at paper for help


Time is still busted, dates are being stored in UTC (invitation), but they aren't be converted to local time.
TIME SOLUTION: Dates AREN'T being stored in UTC, they're being converted to utc by moment (correct so far), then being converted to utc again by the database that thinks it got handed an American/Mountain time. I have to remove the .utc() from the moment time thing, and I have to have a little thing say what the current timezone is. I should also add a timezone field to the User model, I really should.
