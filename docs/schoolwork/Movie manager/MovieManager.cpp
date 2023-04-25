/*
Author: Mateo Topete
ID:89233623
*/
#include "MovieManager.h"
//Function of MovieManager that continually runs until stopped by "q" input from user
//Uses a while loop based on a private boolean variable in the UI and interprets input from functions in MovieManagerUI
void MovieManager::run() {
	cout << "Welcome to Movie Rental Kiosk!" << endl;
	string user_input;
	while (procs.running()) {
		procs.printMenu();
		user_input = procs.getCommand();
		if (user_input == "AM") {
			this->addMovie(Movies(procs.getMovieCode(), procs.getMovieName()));
		}
		if (user_input == "DM") {
			this->discontinueMovie(procs.getMovieCode());
		}
		if (user_input == "RM") {
			this->rentMovie(procs.getMovieCode(), Renter(procs.getRenterID(), procs.getRenterFirstName(), procs.getRenterLastName()));
		}
		if (user_input == "RR") {
			this->returnRental(procs.getRenterID(), procs.getMovieCode());
		}
		if (user_input == "P") {
			this->printInventory();
		}
		if (user_input == "Q") {
			procs.togglerun();
		}
	}
}
//function that adds a movie to the inventory array.
//checks if the movie has any empty fields and that there is room in the inventory as well as if it is a duplicate or not based on the ID of the movie
// if all tests are passed, the total inventory size increases by 1 and the movie is added to the array
void MovieManager::addMovie(Movies mov) {
	try {
		if (mov.getMovieCode() == "" or mov.getMovieName() == "") {
			throw EmptyMovieInfoException();
		}
		if (inventory_size == size(mov_inventory)) {
			for (int i = 0; i < inventory_size; i++) {
				if (mov_inventory[i].getMovieName() == "") {
					mov_inventory[i] = mov;
					return;
				}
			}
			throw MovieLimitException();
		}
		else {
			for (int i = 0; i < inventory_size; i++) {
				if (mov_inventory[i].getMovieCode() == mov.getMovieCode()) {
					throw DuplicateMovieException();
				}
			}
		}
		mov_inventory[inventory_size] = mov;
		inventory_size += 1;
	}
	catch (DuplicateMovieException) {
		cout << "DuplicateMovieException: That movie ID already exists." << endl;
	}
	catch (MovieLimitException) {
		cout << "MovieLimitException: Max movies (20) has been reached" << endl;
	}
	catch (EmptyMovieInfoException) {
		cout << "EmptyMovieInfoException: Movie info cannot be left blank" << endl;
	}
}
//Function for removing movies from the inventory array
// checks that the inventory array actually has objects in it first, the makes sure that no one is currently renting the movie and that the movie does exist within the inventory
// if all tests are passed, the movie is replaced by an empty constructor, the movie array is shifted accordingly, and the total inventory size is reduced by one.
void MovieManager::discontinueMovie(string code) {
	try {
		if (inventory_size == 0) {
			throw EmptyMovieListException();
		}
		else {
			for (int i = 0; i < inventory_size; i++) {
				if (mov_inventory[i].getMovieCode() == code) {
					if (mov_inventory[i].getRentedCopies() != ""){
					throw RentedMovieException();
					}
					mov_inventory[i] = Movies();
					for (int i = 0; i < inventory_size; i++) {
						//this try catch block is left empty to avoid crashing when i+1 goes over the 20 limit for movies. the point is to move over every sinlge object, it is easiest to just go until an error and auto-terminate
						//same as the try-catch in the Movies class, adjusted for the MovieManager class
						try {
							if (mov_inventory[i].getMovieCode() == "") {
								mov_inventory[i] = mov_inventory[i + 1];
							}
						}
						catch (...) {
						}
					}
					inventory_size -= 1;
					return;
				}
			}
			throw MovieNotFoundException();
		}
	}
	catch (MovieNotFoundException) {
		cout << "MovieNotFoundException: Movie does not exist" << endl;
	}
	catch (EmptyMovieListException) {
		cout << "EmptyMovieListException: Movie list is empty" << endl;
	}
	catch (RentedMovieException) {
		cout << "RentedMovieException: Cannot discontinue a movie that has rented copies" << endl;
	}
}
//function to add a renter to a movie's renter array
//checks that the renter information is filled and that the movie exists. checking renter limit is handled within the Movie class
//if all tests are passed then a renter is added to a movie's renter list
void MovieManager::rentMovie(string code, Renter renter) {
	try {
		if (renter.getRenterFirstName() == "" or renter.getRenterLastName() == "") {
			throw EmptyRenterNameException();
		}
		for (int i = 0; i < inventory_size; i++) {
			if (mov_inventory[i].getMovieCode() == code) {
				mov_inventory[i].rentMovie(renter);
				return;
			}
		}
		throw MovieNotFoundException();
	}
	catch (MovieNotFoundException) {
		cout << "MovieNotFoundException: Movie does not exist" << endl;
	}
	catch (EmptyRenterNameException) {
		cout << "EmptyRenterNameException: Cannot leave Renter information blank" << endl;
	}
}
//functiuon for removing a renter from a movie's renter list.
//checks that the renter list for the movie is not empty and that the movie exists; handling valid id and movie code is handled withing the Movie class functions
//if all tests are passed the renter is removed from the movies renter array
void MovieManager::returnRental(int id, string code) {
	try {
		for (int i = 0; i < inventory_size; i++) {
			if (mov_inventory[i].getMovieCode() == code) {
				if (mov_inventory[i].getRentedCopies() == "") {
					throw EmptyRenterListException();
				}
				mov_inventory[i].returnRental(id);
				return;
			}
		}
		throw MovieNotFoundException();
	}
	catch (MovieNotFoundException) {
		cout << "MovieNotFoundException: Movie does not exist" << endl;
	}
	catch (EmptyRenterListException) {
		cout << "EmptyRenterListException: This Movie has not been rented to anyone" << endl;
	}
}
//simple function using the overloaded ostream function within the Movie class to print out information for each movie in the inventory.
void MovieManager::printInventory() {
	for (int i = 0 ; i < inventory_size; i++) {
		cout << this->mov_inventory[i] << endl;
	}
}