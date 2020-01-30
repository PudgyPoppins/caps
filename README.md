# WHENEVER YOU WANT TO START THE VIRTUAL DEV: source ~/.virtualenvs/djangodev/bin/activate

This project doesn't really require a readme (yet), but I'm just keeping this to track progress and see what I need to do...

One thing I should focus on is working outside in.

# TODO:
* see image issue
* ## Forms / views:
	* markdown for the volunteer description would be pretty cool, I think
	* when you refresh the page, all of the field values are kept. However, the address is NOT.

* ## User system / user classess
	* when you go to accounts/profile, it should show your profile if you're logged in, otherwise it'll tell you to sign up or log in
	* you should only be able to delete an object that you've created, unless you're a moderator
	* change the default page if you're signed in or not (signed out, /home, signed in, /networks)
	* show a message when a user signs out
	* override accounts login view so that you can't access it if you're *logged in*, as well as other views
	* create groups
	* ### Reporting System
		* If a nonprofit is flagged true, then send an email with the reason
			* scratch that... first, add a many to many field of reasons, similar to tags, to nonprofits and networks. Then, if they have a reason, it will automatically pop up as flagged in the template view.
		* reports should probably be a separate model that has a many to many relationship with nonprofits and networks, and could be assigned or deleted
* ## Calendar
	* create it
* ## Later:
	* When making the site look good, I'll probably have to override all of the forms with custom elements. See nonprofit_map and change all of that dom element creation stuff that I did.
	* favicon
	* write some general tests
	* ordering networks/nonprofits based on distance to you: https://geopy.readthedocs.io/en/stable/#module-geopy.distance
	* switch image uploading to a service like aws
	* use regex on phone model to enforce an answer
	* add a button you can use to get directions to a nonprofit on its detail view
	* set keywords and author meta for base.html

# Issues
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