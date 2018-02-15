#include <opencv2/opencv.hpp>

using namespace cv;
class ConsoleController : public VideoCapturePeopleCounterDelegate {
public:
    	ConsoleController(const VideoCapturePeopleCounter* counter) {
        	this->counter = counter;
    	}
	~ConsoleController() {
	}
    	void onFrameProcess(const Mat& frame, const Mat& debugFrame) {
		if(this->frameIndex == 0) {
			cout << "frame,entered,exited" << endl;
		}
        	cout << this->frameIndex << "," << counter->peopleWhoEnteredCount << "," << counter->peopleWhoExitedCount << endl;
		frameIndex++;
        }
    	void onFrameWithPersonDetected(const Mat& frame, const Mat& debugFrame, const Person* person) {
	}
	
private:
 	const VideoCapturePeopleCounter* counter;
	int frameIndex = 0; 
};
