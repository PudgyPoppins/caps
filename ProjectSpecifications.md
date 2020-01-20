This file is kind of like the ReadMe #TODO section. However, it's more of like a road map, and what I want to accomplish for this project.
I will NOT do bug reporting in this section

* # Users
* # Networks
	* ## Nonprofits
		* Can be ordered by name, distance away from you, and time created
		* Nonprofit coordinates autogenerate on create.
		* If you change the nonprofits's coordinates in an update, then it shouldn't override them with the geolocator.

		* Alternative, probably better coordinate creation:
			Whenever you enter an address, it opens up a toggles showing a map with a pin. The pin pops up first wherever the geocoder sets it from the address. Then, the user is able to move the pin to a different location on the map to change the coords. The coordinates of the pin (known by mapbox) are passed to invisible coordinate fields using javascript. This will be more intuitive for the user.
	* ## Reporting
