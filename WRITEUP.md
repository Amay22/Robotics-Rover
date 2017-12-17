## Project: Search and Sample Return Writeup
---

### Notebook Analysis

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
And another! 

- Images from the rover were used to identify the obstacles, samples and navigable terrain based on color.
- Transformed all the images to using the built-in cv2.getPerspectiveTransform() and then wrap the source and destination coordinates using cv2.warpPerspective(). The source and destination were already derived from images in the calibration_images folder.
- Use the color thresholding function to identify the rock, ground, and blocked pixels. To identify the navigable terrain I took the pixels inside the threshold i.e. (RGB= 160, 160, 160). To get the obstacle I used the inverse of the the navigable terrain.
- Convert these naviagable terrain, obstacle and rock samples to rover coordinates.
- Translate the rover coordinates to world map coordinates.
- Add the pixel location in world coordinates to the image map that  gives out the rock, ground, and blocked pixels their own respective unique identifying color.

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

Copied over from the python Notebook 'process_image()' function that is described in the function above.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

1. If x, y position, and heading of the rover is different from the last recorded position we can say that we've sufficiently moved. Keep moving in the same direction.
2. If x,y position are stuck then turn in position by an angle ranging from -15 to 15 degrees and move forward again.