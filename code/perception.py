import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

# Converts image to from RBG to HLS
# Identify pixels above the threshold above and below given thresholds
def filter_hls_thresholding(img, thresh_min, thresh_max, height = None):

    hls_img = img.copy() # make a copy
    cv2.cvtColor(hls_img, cv2.COLOR_BGR2HLS) # convert image to hls

    # an array of zeros same xy size as img, but single channel
    binary_img = np.zeros_like(img[:,:,0])

    # Require that each pixel be above all three threshold values in HLS
    # within_thresh will now contain a boolean array with "True" where threshold was met
    within_thresh = (hls_img[:,:,0] >= thresh_min[0]) & (hls_img[:,:,0] <= thresh_max[0]) & \
                    (hls_img[:,:,1] >= thresh_min[1]) & (hls_img[:,:,1] <= thresh_max[1]) & \
                    (hls_img[:,:,2] >= thresh_min[2]) & (hls_img[:,:,2] <= thresh_max[2])

    # Index the array of zeros with the boolean array and set to 1
    binary_img[within_thresh] = 1

    if height is not None:
        binary_img[:height, :] = 0

    return binary_img

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    pos_x, pos_y, yaw, img = Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.img
    world_size, scale = 200, 30
    # 1) Define source and destination points for perspective transform
    destination_points = np.float32([[155, 155], [165, 155], [165, 145], [155, 145]])
    source_points = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    # 2) Apply color threshold to identify navigable terrain/obstacles/rock samples
    hls_threshold_ground_img = filter_hls_thresholding(img, thresh_min=(0, 100, 70), thresh_max=(255, 255, 255), height=70)
    hls_threshold_obstacle_img = filter_hls_thresholding(img, thresh_min=(0, 0, 0), thresh_max=(255, 100, 255))
    hls_threshold_rock_img = filter_hls_thresholding(img, thresh_min=(0, 100, 0), thresh_max=(255, 255, 70))
    
    # 3) Apply perspective transform
    warped_ground_img = perspect_transform(hls_threshold_ground_img, source_points, destination_points) 
    warped_obstacle_img = perspect_transform(hls_threshold_obstacle_img, source_points, destination_points) 
    warped_rock_img = perspect_transform(hls_threshold_rock_img, source_points, destination_points)
    
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image = Rover.vision_image * 0
    y_warped_ground, x_warped_ground = warped_ground_img.nonzero()
    Rover.vision_image[y_warped_ground, x_warped_ground, 0] = 255
    y_warped_obstacle, x_warped_obstacle = warped_obstacle_img.nonzero()
    Rover.vision_image[y_warped_obstacle, x_warped_obstacle, 2] = 255
    y_warped_rock, x_warped_rock = warped_rock_img.nonzero() 
    Rover.vision_image[y_warped_rock, x_warped_rock, 1] = 255

    # 5) Convert map image pixel values to rover-centric coords
    x_ground, y_ground = rover_coords(warped_ground_img)
    x_obstacle, y_obstacle = rover_coords(warped_obstacle_img)
    x_rock, y_rock = rover_coords(warped_rock_img)
    # 6) Convert rover-centric pixel values to world coordinates
    x_ground_world, y_ground_world = pix_to_world(x_ground, y_ground, pos_x, pos_y, yaw, world_size, scale)
    x_obstacle_world, y_obstacle_world = pix_to_world(x_obstacle, y_obstacle, pos_x, pos_y, yaw, world_size, scale)
    x_rock_world, y_rock_world = pix_to_world(x_rock, y_rock, pos_x, pos_y, yaw, world_size, scale)
    
    # 7) Update Rover worldmap (to be displayed on right side of screen)
    Rover.worldmap[y_ground_world, x_ground_world, 2] = 255
    Rover.worldmap[y_obstacle_world, x_obstacle_world, 0] = 255
    Rover.worldmap[y_rock_world, x_rock_world, 1] = 255
    
    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles  
    dists, angles = to_polar_coords(x_ground, y_ground)
    
    Rover.found_rock = False
    if len(x_rock) > 2:
        print("Rock Found")
        Rover.found_rock = True
        dists, angles = to_polar_coords(x_rock, y_rock)

    Rover.nav_dists, Rover.nav_angles = dists, angles
    Rover.ground_pixels_count = len(x_ground)
    x_mean, y_mean = x_warped_ground, y_warped_ground
    if Rover.found_rock:
        x_mean, y_mean = x_warped_rock, y_warped_rock
    # cv2.line(Rover.vision_image, (160, 160),(x_mean, y_mean), [0, 255, 0], 3)
    return Rover