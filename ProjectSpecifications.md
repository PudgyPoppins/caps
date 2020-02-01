This file is kind of like the ReadMe #TODO section. However, it's more of like a road map, and what I want to accomplish for this project.
I will NOT do bug reporting in this section

* # Users
	* ## Groups
		* Nonprofit representatives: these people can claim a nonprofit (maybe a fk relationship? Multiple people per one np?) by clicking a claim button on the nonprofit page. After they verify themselves with a moderator, they can add events onto the nonprofit page. On their profile page, I want something akin to a twitter verification check mark to appear
			* when a nonprofit rep claims a nonprofit, it becomes "locked", and it can't be changed anymore
		* moderators: get reports of flagging, can delete anything, etc
			* moderators can also retrieve items that were deleted within the last month and reinstate them. Later than that, and it gets perma-deleted
		* base users:
	* ## Reporting
* # Networks
	* ## Nonprofits
		* Can be ordered by name, distance away from you, and time created

		* Whenever you enter an address, it opens up a toggles showing a map with a pin. The pin pops up first wherever the geocoder sets it from the address. Then, the user is able to move the pin to a different location on the map to change the coords. The coordinates of the pin (known by mapbox) are passed to invisible coordinate fields using javascript. This will be more intuitive for the user.
* # Calendar
	* If you are a nonprofit representative, you can add volunteer events to a calendar, which other users will be able to see
	* Models (Event):
		* start_time, end_time, repeat (choice field), title, description, nonprofit (foreign key), network (foreign key)
	* An event can have a nonprofit fk or a network fk, or no fk, but it cannot have both
	* I want to be able to display an HTMLcalendar, as well as a list of events
	* Events can repeat weekly or monthly | https://www.kpcw.org/community-calendar#stream/0
