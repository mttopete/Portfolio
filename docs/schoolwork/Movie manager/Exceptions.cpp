/*
Author: Mateo Topete
ID:89233623
*/
#include <exception>
#include <string>
#include <iostream>
using namespace std;
//Simple decleration of different types of exception names for use in the other files
class DuplicateMovieException :public exception {
};
class MovieLimitException :public exception {
};
class EmptyMovieInfoException :public exception {
};
class MovieNotFoundException :public exception {
};
class EmptyMovieListException :public exception {
};
class EmptyRenterListException :public exception {
};
class RenterLimitException :public exception {
};
class RenterNotFoundException :public exception {
};
class DuplicateRenterException :public exception {
};
class InvalidRenterIDException :public exception {
};
class EmptyRenterNameException :public exception {
};
class RentedMovieException :public exception {
};
