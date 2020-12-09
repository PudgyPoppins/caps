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
		* Scratch that... anyone can add an event to a nonprofit, but it'll show up as unverified, which means that you have to toggle a button to be able to see it, and there'll be a little warning on it
	* Events can repeat weekly or monthly | https://www.kpcw.org/community-calendar#stream/0
	* when a user gets created, they automatically have a calendar for themselves created, too. Same goes for nonprofits and networks.
		* Users can add their personal events to their personal calendar
	* There's also a global calendar that has general events for the entire website (planned site maintenance, Mitzvah Day, etc). I can't really think of any big global events, but it'd be nice to have.
* # Organizations
	* Organizations are groups of users that can bring in networks and nonprofits into their organization. They can have specific hour requirements for over a period of time, and can host their own events.
	* Organizations can subscribe to certain calendars (just like users), and they can also add their own events
* # Logging
	* You can log hours that you've completed for yourself, and write a description of the work that you did
	* If a nonprofit has a verified representative, then you can put them as who you volunteered for, then they can confirm that you did volunteer there
	* Users can add logs from their profile. Users search for a nonprofit, and if one isn't found, then they get prompted to create one.
		* if that nonprofit does exist, but it doesn't have any reps, then prompt them to notify that nonprofit
