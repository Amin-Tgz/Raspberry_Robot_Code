#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
using namespace cv;
using namespace std;
int main(void)
{
    VideoCapture cap(0); // open the default camera
    if(!cap.isOpened())  // check if we succeeded
        cout << "no camera";
    Mat edges;
    namedWindow("edges",1);
    while(1)
    {
        Mat frame;
        cap >> frame; // get a new frame from camera
        imshow("edges", frame);
        if(waitKey(30) >= 0) break;
    }
    return 0;
}