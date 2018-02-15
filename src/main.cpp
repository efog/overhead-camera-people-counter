#include "help.cpp"
#include "modules/counter.hpp"
#include "modules/console.hpp"

int main(int argc, char* argv[]) {
    if (argc != 2) return help();

    VideoCapturePeopleCounter* counter = new VideoCapturePeopleCounter(argv[1]);
    counter->delegate = new ConsoleController(counter);
    counter->setRefLineY(120);
    counter->start();
}
