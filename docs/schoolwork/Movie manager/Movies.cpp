/*
Author: Mateo Topete
ID:89233623
*/
#include "Movies.h"
//simple retrieval functions for Movie objects
string Movies::getMovieCode() {
	return code;
};

string Movies::getMovieName() {
	return movie_name;
};

string Movies::getRentedCopies() {
	string outstr = "";
	for (int i = 0; i < copies; i++) {
		outstr += "  " + Renters[i].getRenterFirstName() + " " + Renters[i].getRenterLastName() + " ID:" + to_string(Renters[i].getRenterID()) + "\n";
	}
	return outstr;
};
//Rent Movie function, checks for a valid renter id, makes sure that there are not too many rented copies and that there are no duplicates
//If all tests are passed then the renter is added to the array the the helper function is called to sort out the list
void Movies::rentMovie(Renter renter) {
	try {
		if (renter.getRenterFirstName() == "" or renter.getRenterLastName() == "") {
			throw EmptyRenterNameException();
		}
		if (copies == size(Renters)) {
			throw RenterLimitException();
		}
		if (renter.getRenterID() < 0) {
			throw InvalidRenterIDException();
		}
		for (int i = 0; i < copies; i++) {
			if (renter.getRenterID() == Renters[i].getRenterID()) {
				throw DuplicateRenterException();
			}
		}
		Renters[copies] = renter;
		copies += 1;
		helpSort();
	}
	catch (RenterLimitException) {
		cout << "RenterLimitException: Max number of copies (10) are already being rented" << endl;
	}
	catch (DuplicateRenterException) {
		cout << "DuplicateRenterException: This person has already rented this movie" << endl;
	}
	catch (InvalidRenterIDException) {
		cout << "InvalidRenterIDException: ID must greater than zero" << endl;
	}
	catch (EmptyRenterNameException) {
		cout << "EmptyRenterNameException: Cannot leave Renter information blank" << endl;
	}
};
//Return Rental function, checks for valid ID and that the renter exists withing the Renters array
//If all tests are passed then the renter is removed from the array, the total copies is decreased by one and the objects in the array are shifted accordingly.
void Movies::returnRental(int id) {
	try {
		if (id < 0) {
			throw InvalidRenterIDException();
		}
		for (int i = 0; i < copies; i++) {
			if (Renters[i].getRenterID() == id) {
				Renters[i] = Renter();
				for (int i = 0; i < copies; i++) {
					//this try catch block is left empty to avoid crashing when i+1 goes over the 10 limit for renters. the point is to move over every sinlge object, it is easiest to just go until an error and auto-terminate
					try {
						if (Renters[i].getRenterID() == 0) {
							Renters[i] = Renters[i + 1];
						}
					}
					catch (...) {
					}
				}
				copies -= 1;
				return;
			}
		}
		throw RenterNotFoundException();
	}
	catch (RenterNotFoundException) {
		cout << "RenterNotFoundException: There is no one with that ID renting this movie" << endl;
	}
	catch (InvalidRenterIDException) {
		cout << "InvalidRenterIDException: ID must greater than zero" << endl;
	}
};
//A helper sorting function to free up clutter within the main functions. First compares first names, then last names, and finally ids when sorting.
//Finds the lowest alphabeticly or numerically by using the .compare functon of strings or > for id's.
//selection sort based
void Movies::helpSort() {
	Renter Low = Renters[0],blank;
	int temp = 0,temp2 = 0;
	while (temp < copies) {
		for (int i = temp; i < copies; i++) {
			if (Low.getRenterFirstName() == " ") {
				Low = Renters[i];
			}
			if (Low.getRenterFirstName().compare(Renters[i].getRenterFirstName()) >= 0) {
				if (Low.getRenterLastName().compare(Renters[i].getRenterLastName()) >= 0) {
					if (Low.getRenterID() > Renters[i].getRenterID()) {
						if (Renters[i].getRenterID() != 0) {
							temp2 = i;
							Low = Renters[i];
						}
					}
				}
				else {
					temp2 = i;
					Low = Renters[i];
				}
			}
		}
		blank = Renters[temp];
		Renters[temp] = Low;
		Renters[temp2] = blank;
		temp += 1;
		Low = Renters[temp];
		temp2 = temp;
	}
};
//overloading the << operator in ostream to print out movie info in the MovieManager class.
ostream& operator << (ostream& os, Movies& mov) {
	string outstr;
	outstr += mov.getMovieName() + " Code:" + mov.getMovieCode() + "\n"
		+ " Current renters: " + "\n" + mov.getRentedCopies() + "\n";
	os << outstr;
	return os;
}