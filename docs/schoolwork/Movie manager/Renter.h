/*
Author: Mateo Topete
ID:89233623
*/
#ifndef RENTER_H_
#define RENTER_H_

#include "Exceptions.cpp"

class Renter {
private:
	string first_name, last_name;
	int id;
public:
	//Default constructor and a typed constructor for Renters
	Renter() {
		first_name = " ";
		last_name = " ";
		id = 0;
	};
	Renter(int id, string first_name, string last_name) {
		this->first_name = first_name;
		this->last_name = last_name;
		this->id = id;
	};
	void setRenterID(int);
	int getRenterID();
	void setRenterFirstName(string);
	string getRenterFirstName();
	void setRenterLastName(string);
	string getRenterLastName();
};
#endif
