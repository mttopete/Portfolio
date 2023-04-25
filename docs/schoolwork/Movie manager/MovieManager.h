/*
Author: Mateo Topete
ID:89233623
*/
#ifndef MOVIEMANAGER_H_
#define MOVIEMANAGER_H_

#include "MovieManagerUI.h"
class MovieManager {
private:
	Movies mov_inventory[20];
	int inventory_size;
	MovieManagerUI procs;
public:
	MovieManager() {
		inventory_size = 0;
	};
	void run();
	void addMovie(Movies);
	void discontinueMovie(string);
	void rentMovie(string, Renter);
	void returnRental(int, string);
	void printInventory();
};
#endif
