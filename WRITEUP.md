## Project: Search and Sample Return Writeup

[//]: # (Image References)
[image1]: ./output/camera.png
[image2]: ./output/hls_thresholded.png
[image3]: ./output/warped.png
[image4]: ./output/steering_angle.png
---

### Notebook Analysis

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
And another! 

- Images from the rover were used to identify the obstacles, samples and navigable terrain based on color.
- I converted the image in BGR format to HLS format as yellow is way easier to distinguish this format. Navigable Terrain is of light brownish color which is high lightness and shows up white after thresholding correctly. Obstacles are of dark brownish color which has a low lightness. Rock samples are of yellowish color, which has a high lightness and low saturation.
- Transformed all the images to using the built-in cv2.getPerspectiveTransform() and then wrap the source and destination coordinates using cv2.warpPerspective(). The source and destination were already derived from images in the calibration_images folder.
- Use the color thresholding function to identify the rock, ground, and blocked pixels. To identify the navigable terrain I took the pixels inside the threshold for navigable terrain, obstacle and rock sample separately for better clarity.
```python
navigable_terrain_threshold_min = (0, 100, 70)
navigable_terrain_threshold_max = (255, 255, 255)

obstacle_threshold_min = (0, 0, 0)
obstacle_threshold_max = (255, 100, 255)

rock_threshold_min = (0, 100, 0)
rock_threshold_max = (255, 255, 70)

```
- Transform the image into bird's view (sky view) using `cv2.getPerspectiveTransform(src_points, dst_points)` and `cv2.warpPerspective(img, transform_matrix, dimensions)`. This gives us a warped image which can be used to get rover's location. 
```python
src_points = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
dst_points = np.float32([[155, 155], [165, 155], [165, 145], [155, 145]])
```
- Convert the warped image to rover coordinates using `get_rover_coordinates()` function.
- Once we get rover coordinates we can place the rover on the `world_map` using the `convert_rover_to_world_coordinates()` function.
- Add this pixel location to world coordinates of the image map. We can also color code navigable terrain, obstacle and rock samples.


![alt text][image1]

![alt text][image2]

![alt text][image3]

![alt text][image4]

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.

- `perception_step()` gets passed in the Rover object which contains pretty much everything we need Rover camera image, Rover position, angle and yaw and more.
- Once I got the Rover image I did exactly as mentioned above I processed the image through HLS filter, then thresholding, then perspective transform to get the the different objects in the image that required namely: navigable terrain (ground), Obstacle (blocked) and Rock Samples that we gotta pick up. 
- Convert the warped image that we get from perspective transform is used to get the current rover coordinates using `get_rover_coordinates()` function. we can use the rover coordinates to get the polar coordinates. 
- These polar coordinates are used to compute the mean angle that can be used as the angle of steering for the rover.
- The world pixels are transformed from the rover coordinates to world map size using a scale of 30 and world size of 200.
- The world pixels locations are added to the image map, giving rock, ground, and blocked pixels their own respective unique identifying color.
- The mean pixel location of the ground or rock (more preferable) if it exist is used to draw a line from from the bottom center of our rover image to the rock or the forward ground to give us a angle of the direction the rover should be steering towards. In all cases Rock is more preferable to steer towards.
- If in the image we can spot a rock we update the property Rover.found_rock to True and also steering angle Rover.angle to approximate itself to go in the direction of the rock.

#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

1. mode = forward : If x, y position, and heading of the rover is different from the last recorded position we can say that we've sufficiently moved. Make sure that we record the current position to check in the next iteration. Keep moving in the same direction if there's navigable terrain ahead. Explained above the angle for navigable terrain.
2. rock_found = True: If the image has a rock sample then we should it then we should change the steering angle to go towards it and we should lower our speed and keep move towards the rock. If we are very close to the rock then we should stop the vehicle and pickup the rock. We effectively go into mode = stop.  
3. mode = stop : If we have not completely stopped keep braking. If we are braking then it's either because we have found a rock or we have reached an obstacle. If it's a rock do the step 2. If we have found an obstacle then we should check for navigable terrain and whereever we have the most amount (farthest) of navigable terrain we should change our steering angle in that direction.
4. mode = stuck : The rover is completely capable of rotating on spot so if we get stuck we can't turn left or right we should rotate in spot until we find some navigable terrain and steer in that direction.


#### Issues and Future Performance improvements

- In the middle where all paths meet I have seen the rover picks a turning angle and get stuck in circular loop.
- There are some spots on the map that cause the rover to get collosaly stuck. Technically the rover should not be even going to an area where it can see no way out of like a dead end.
- Rat in a maze problem should be solved on the rover. We have a world map and all the traversed routes as well but the rover doesn't keep any memory of the paths traversed and keeps going to the same spot over and over again.
- I have kept the speed very slow and we can speed up the traversal and save time.
- The code quality is not good for decision it's just a bunch of modes and if blocks.
