# WHENEVER YOU WANT TO START THE VIRTUAL DEV: source ~/.virtualenvs/djangodev/bin/activate

This project doesn't really require a readme (yet), but I'm just keeping this to track progress and see what I need to do...

One thing I should focus on is working outside in.

# TODO:
* ## Forms:
	* when you get prompted with the coordinates, you should be able to move a point on a map to select them, or when you enter the title, it should then move the map to the coords it'll generate
	* this may help with next step: https://stackoverflow.com/questions/25457695/django-must-have-at-least-one-form-field-filled-in#26292412
	* Require at least one of the website, email, address forms to be filled out for nonprofits

* ## User system / classess
	* create it
	* ### Reporting System
		* If a nonprofit is flagged true, then send an email with the reason
			* scratch that... first, add a many to many field of reasons, similar to tags, to nonprofits and networks. Then, if they have a reason, it will automatically pop up as flagged in the template view.
		* flag nonprofits and networks that can't generate coordinates due to timeout errors with a reason there
		* reports should probably be a separate model that has a many to many relationship with nonprofits and networks, and could be assigned or deleted
* ## Later:
	* favicon
	* write some general tests
	* ordering networks/nonprofits based on distance to you: https://geopy.readthedocs.io/en/stable/#module-geopy.distance
	* switch image uploading to a service like aws

# Issues
* potential issue: networks, "Lisbon, Peru" and "Lisbon Peru" can be created because they have technically different titles (comma vs no comma), but they have the same slug
* potential issue: image gets resized every time it is saved if it's above a certain width. While I set this to 100% conversion, I'm curious if future loss occurs

# What was done
* 12/30 added tests, static files, tagging, the flagged attribute to both network and nonprofit, and changed the admin site
* 12/31 added views for adding a network and looked into forms
* 1/1 added the network change, update, and delete forms + views / urls
* 1/4 WOO! Checkboxes for tags, now you can get coordinates for networks just by adding them, etc.
* 1/7 two network forms for createview and updateview now, nonprofit forms are coming along. Found more issues
* 1/12 detail network view now uses an actual generic detail view, found and fixed a slug error (slugs are now unique with the scope of the individual network), and now nonprofit detail views and delete views kind of work... now reverses back to detail view after updating
* 1/16 nonprofit delete view and detail view now work even if name is duplicated, found and fixed other non detail view bug, changed view success redirects, fixed tags not showing up, and switched to github.
* 1/18 - 1/19 asked a fire stackoverflow questions, coords now need address to generate and have to be None type previously, changed geocoder to MapBox, foreign key is automatically created when you add a nonprofit, update form differs from create form for nonprofit (prescence of network field), added image uploads, and automatic image resizing. Only src_link or src_file can be filled, not both.