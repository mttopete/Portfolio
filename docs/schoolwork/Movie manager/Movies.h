/*
Author: Mateo Topete
ID:89233623
*/
#ifndef MOVIES_H_
#define MOVIES_H_

#include "Renter.h"
class Movies {
private:
	int copies;
	string movie_name,code;
	Renter Renters[10];
public:
	//default constructor and typed constructor for Movies
	Movies() {
		code = "";
		copies = 0;
	};
	Movies(string code, string movie_name) {
		this->code = code;
		this->movie_name = movie_name;
		copies = 0;
	}
	string getMovieCode();
	string getMovieName();
	string getRentedCopies();
	void rentMovie(Renter);
	void returnRental(int);
	void helpSort();
	friend ostream& operator <<(ostream& os, Movies&);
};
#endif
