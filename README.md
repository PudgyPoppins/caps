# WHENEVER YOU WANT TO START THE VIRTUAL DEV: source ~/.virtualenvs/caps/bin/activate
# source env/bin/activate

This project doesn't really require a readme (yet), but I'm just keeping this to track progress and see what I need to do...

One thing I should focus on is working outside in.

This might come in handy for providing back links: <a href="javascript:history.go(-1)">back</a>

# TODO:
* ## Network / Nonprofits
	* done, for minimum viable product

	* soft deleting as an option (a moderator could recover a deleted object up to 2 weeks later or so) | https://medium.com/@adriennedomingus/soft-deletion-in-django-e4882581c340 | this one is probably better: https://blog.khophi.co/soft-delete-django-quickly/
	* ### Forms
		* markdown for the volunteer description would be pretty cool, I think
		* when you refresh the page, all of the field values are kept. However, the address is NOT.

* ## Users
	* Email verification

* ## Reporting System
	* Literally just copy/paste the reporting system I had for APCrowd2020

* ## Calendar
	* rrule form
	
	* import events from a google cal | https://fullcalendar.io/docs/v3/google-calendar
	* rss feeds

* ## Organizations
	* hour goals
	* add goals to user profiles when they get created, if they're in an organization

	* Organizations are a way for groups of users to connect to specific nonprofits and networks
	* Organizations have leaderboards where they sort who has the most hours in their logging (verified plus verified and unverified scores)

	* add invite to moderator links?

* ## Logging
	* When a user signs up for an event, after the event has happened, then the nonprofit representative can verify that they helped out
		* Add another crontab job that runs every 30 minutes. Filter for all of the volunteering events that happened more than one day ago. Send one email to nonprofit reps listing all of the attendees who didn't have their hours verified so far.
	* Nonprofit representatives can also add a log for a user without an event
	* Users can add their own logs. They can select a nonprofit that's already added or write in their own. They can write in their hours, too.

	* Should logs show up on user calendars as events?

* ## Getting ready for launch:
	* css top to bottom
	* will need to override most forms, make them look nice and pretty

	* Change DEBUG to TRUE
	* Get a real email address to use
	* robots.txt / meta descriptors on base.html
	* Migrate project to a server computer / add crontab jobs specified in the management scripts / wipe sql database
	* Minimize external css/js loaded on each page to minimize requests
	* Add pretty good caching to Nginx

* ## Later:
	* 404 error page isn't getting css.
	* When making the site look good, I'll probably have to override all of the forms with custom elements. See nonprofit_map and change all of that dom element creation stuff that I did.
	* make more favicons (for phones) and more meta data (twitter card, etc)
	* write some general tests
	* ordering networks/nonprofits based on distance to you: https://geopy.readthedocs.io/en/stable/#module-geopy.distance
	* add a button you can use to get directions to a nonprofit on its detail view
	* set keywords and author meta for base.html

# Issues
* if you refresh a network when you're creating it, the coords will reset while the title stays, which isn't good. I should clear the forms on page reload for this view.
* whenever you add a nonprofit with the same name in the same network, it rightfully raises an error, but not in the form view which is what I want
* issue: networks, "Lisbon, Peru" and "Lisbon Peru" can be created because they have technically different titles (comma vs no comma), but they have the same slug
* original big image doesn't get delted after resizing happens
	* I haven't seen this happen again, though, Oct 21

# Brainstorming
* 

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
* 10/14 Added a few fields and a property to Attendee. Created an unattend view. Automatically email users whenever they sign up for an event. Added an email template for use in confirming sign ups. Created a management tool to automatically send emails to people who have volunteering things happening soon. Created a command for a cronjob (that I have commented out on the management tool since Arch Linux) to do this.
* 10/20 Completed the nonprofit rep form, everything's working, EXCEPT for image uploads :(. This is NOT a pog champ moment >:(. It also automatically send admin emails when users apply, and gives users emails if they get accepted. Admins can approve applicants on the admin page.
* 10/21 Got images to work! This is true for both nonprofits, networks, and applicants. Epic gamer moment! Listed representing nonprofits on user's profile page. Simplified profile page context variables with reverse relationships. Added more detail on the nonprofit_rep template. Stopped user from applying if they're already representing the nonprofit. Set the home page for nonprofit reps to their nonprofit. Added nonprofit success messages. Added a regex phone validator
* 10/28 Added locked boolean to nonprofits. Added a system for nonprofit reps to lock their nonprofits from user-edits and user-created calendar events, and unlock them.
* 10/29 Added a way for nonprofit reps to verify/unverify events. Changed the calendar json to show only verified events, and show all events if ?all is present in the url. Need to add a way to filter with fullcalendar, still, but we're getting close. Removed bulma. Actually added filter with fullcalendar later today, but will add in next commit.
* 11/1 Locked nonprofits by default after approving a nonprofit rep. Made it so that organization leaders can subscribe/unsub from calendars for their organization. Worked on creating announcements for nonprofits.
* 11/2 Added announcements / replies for nonprofit reps. Did some work on the TextPost model. Added recursive replies! (That wasn't in the minimum viable product, those nonprofits better be grateful, smh)
* 11/10 It's been a hot sec, but I got announcements working for organizations, too. I spent some time rewriting the announcement code to make it shared between nonprofits / orgs, and I'm happy with the results. I also added some new properties to the organization model to slim down the views and template code, a bit.
* 11/12 Made it so that invites expire after a duration of time, which will be easier to do timezone stuff with. Feelin' pretty proud of that idea. Wrote a manage.py command to invalidate invite links, and wrote a crontab commented out under it. Added an invite user to organization link in the profile view. Made it so that adding users to organization via invite sent them an email. Made it so that orgs could "pin" nonprofits/networks (by subscribing to their calendar).
* 12/8 It's been a sec again, haha. Fixed an error where calendars overzealously tried to exclude other calendars. Fixed a small error where joined orgs were being listed twice on the user profile page. Combined the get_profile and current_profile views into one, better view simply called 'profile'. Added the model for logging. Created a form to add personal logs. Added a search view on network to search for nonprofits with AJAX. Successfully implemented AJAX, but still need to add a way to set the nonprofit from the results.

TODO: 
	* event create view
		* rrule selector
			* look at paper for help
		* event_update, event_form, event.js...


Time is still busted, dates are being stored in UTC (invitation), but they aren't be converted to local time.
TIME SOLUTION: Dates AREN'T being stored in UTC, they're being converted to utc by moment (correct so far), then being converted to utc again by the database that thinks it got handed an American/Mountain time. I have to remove the .utc() from the moment time thing, and I have to have a little thing say what the current timezone is. I should also add a timezone field to the User model, I really should.
