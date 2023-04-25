/*
Author: Mateo Topete
ID:89233623
*/
//function that prints out the main menu for the program
#include "MovieManagerUI.h"
  void MovieManagerUI::printMenu() {
	cout << endl << "----------" << endl;
	cout << endl << "am: Add Movie" << endl;
	cout << endl << "dm : Discontinue Movie" << endl;

	cout << endl << "rm : Rent Movie" << endl;
	cout << endl << "rr : Return Rental" << endl;
	cout << endl << "p : Print Movie Inventory" << endl;
	cout << endl << "q : Quit Program" << endl;
	cout << endl << "----------" << endl;
	cout << endl << "Enter Command :" << endl;
};
  //simple user input retrieval and interpretation functions.
  //each function takes in user input and (where applicable) runs it through the toUpper function to make the input case-insensitive.
  string MovieManagerUI::getCommand() {
	  string command;
	  cin >> command;
	  return toUpper(command);
};
  string MovieManagerUI::getMovieName() {
	  string mname;
	  cout << "Enter the name of the Movie:" << endl;
	  cin.ignore();
	  getline(cin, mname);
	  return toUpper(mname);
};
  string MovieManagerUI::getMovieCode() {
	  string mcode;
	  cout << "Enter the Movie Code" << endl;
	  cin >> mcode;
	  return toUpper(mcode);
};
  int MovieManagerUI::getRenterID() {
	  int oid;
	  cout << "Enter the Renter ID" << endl;
	  cin >> oid;
	  return oid;
};
  string MovieManagerUI::getRenterFirstName() {
	  string fname;
	  cout << "Enter the Renter's first name" << endl;
	  cin >> fname;
	  return toUpper(fname);
};
  string MovieManagerUI::getRenterLastName() {
	  string lname;
	  cout << "Enter the Renter's last name" << endl;
	  cin >> lname;
	  return toUpper(lname);
};
  // function that takes all input and returns it in upper case letters for interpretation by other functions in the MovieManager class
  string MovieManagerUI::toUpper(string com) {
	  string outstr;
	  int x = com.length();
	  for (int i = 0; i < x; i++) {
		  outstr += toupper(com[i]);
	  }
	  return outstr;
};
  // function to return true/false if the program should continue running or not, default true.
  bool MovieManagerUI::running() {
	  return is_running;
};
  //function to toggle the private is_running from true and false to start and stop the program. mostly to stop when "q" is input.
  void MovieManagerUI::togglerun() {
	  is_running = -1*is_running;
};