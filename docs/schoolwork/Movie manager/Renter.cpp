/*
Author: Mateo Topete
ID:89233623
*/
#include "Renter.h"
//Simple set/retrieve functions for private variables
void Renter::setRenterID(int id) {
	this->id = id;
};
int Renter::getRenterID() {
	return id;
};
void Renter::setRenterFirstName(string first_name) {
	this->first_name = first_name;
};
string Renter::getRenterFirstName() {
	return first_name;
};
void Renter::setRenterLastName(string last_name) {
	this->last_name = last_name;
};
string Renter::getRenterLastName() {
	return last_name;
};