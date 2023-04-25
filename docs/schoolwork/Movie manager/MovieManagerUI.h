/*
Author: Mateo Topete
ID:89233623
*/
#ifndef MOVIEMANAGERUI_H_
#define MOVIEMANAGERUI_H_

#include "Movies.h"
class MovieManagerUI {
private:
	bool is_running;
public:
	MovieManagerUI() {
		is_running = true;
	};
	void printMenu();
	string getCommand();
	string getMovieName();
	string getMovieCode();
	int getRenterID();
	string getRenterFirstName();
	string getRenterLastName();
	string toUpper(string);
	bool running();
	void togglerun();
};
#endif
