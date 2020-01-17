# WHENEVER YOU WANT TO START THE VIRTUAL DEV: source ~/.virtualenvs/djangodev/bin/activate

This project doesn't really require a readme (yet), but I'm just keeping this to track progress and see what I need to do...

One thing I should focus on is working outside in.

# TODO:
* **DO THIS!** SWITCH TO GITHUB/GIT, then stop updating the 'what was done' section and just rely on commits
* ordering networks/nonprofits based on distance to you: https://geopy.readthedocs.io/en/stable/#module-geopy.distance
* in the views.py add the network foreign key to the nonprofit being added
* a form so that you can add nonprofits / networks from site ** depending on usership **
* Reporting system
	* If a nonprofit is flagged true, then send an email with the reason
	* flag nonprofits and networks that can't generate coordinates due to timeout errors with a reason there
	* reports should probably be a separate model that has a many to many relationship with nonprofits and networks, and could be assigned or deleted
* Log ins / User system
* For the forms, you can only fill out either src_link or src_file. You can't do both. | this may help: https://stackoverflow.com/questions/25457695/django-must-have-at-least-one-form-field-filled-in#26292412
* Similarly, require at least one of the website, email, location forms to be filled out for nonprofits
* favicon

# Issues
* nonprofit / network errors:
	* *MAYBE* you could have a 'lock coords' option that stops coords from being generated after checking it
	* cleaning pub_date doesn't work if the user sets the pub_date
	* if the user specifys the coordinates themselves, it just immediately overrides them anyways with the geocoder
	* the coords still try to generate even if there is no address to make them with
	* line 86, 'NoneType' object has no attribute 'latitude' but this only occurs when the geocoder is set to use the address, not the title
	* adding a nonprofit or updating a network can't redirect to the detail page

# What was done
* 12/30 added tests, static files, tagging, the flagged attribute to both network and nonprofit, and changed the admin site
* 12/31 added views for adding a network and looked into forms
* 1/1 added the network change, update, and delete forms + views / urls
* 1/4 WOO! Checkboxes for tags, now you can get coordinates for networks just by adding them, etc.
* 1/7 two network forms for createview and updateview now, nonprofit forms are coming along. Found more issues
* 1/12 detail network view now uses an actual generic detail view, found and fixed a slug error (slugs are now unique with the scope of the individual network), and now nonprofit detail views and delete views kind of work... now reverses back to detail view after updating
* 1/16 nonprofit delete view and detail view now work even if name is duplicated, found and fixed other non detail view bug, changed view success redirects, fixed tags not showing up