import numpy as np
import cv2
from skimage.feature import local_binary_pattern
import os
import shutil
import random
from sklearn.model_selection import train_test_split

#SPLIT THE DATASET INTO TRAIN AND TEST FOLDERS
    
# Input paths for both classes
input_dirs = {
    "Generated": "../data/raw/Generated",
    "Real": "../data/raw/Real"
}

# Output base directory
output_dir = "../data/Split_Images"
train_dir = os.path.join(output_dir, "train")
val_dir = os.path.join(output_dir, "val")

# Clean output directories if needed
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

# Limit and split ratio
max_images_per_class = 25000
train_ratio = 0.8  # 80% train, 20% validation

for class_name, class_path in input_dirs.items():
    if not os.path.isdir(class_path):
        print(f"Directory not found for class '{class_name}': {class_path}")
        continue

    # Collect image files only
    all_files = [
        os.path.join(class_path, f)
        for f in os.listdir(class_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if not all_files:
        print(f"No image files found in {class_path}")
        continue

    # Permanently remove excess images if more than 25k (randomly)
    if len(all_files) > max_images_per_class:
        keep_files = set(random.sample(all_files, max_images_per_class))
        delete_files = set(all_files) - keep_files

        for file_path in delete_files:
            os.remove(file_path)
        all_files = list(keep_files)
        print(f"[{class_name}] Randomly removed {len(delete_files)} images to keep only 25,000.")

    # Train/Val split
    train_files, val_files = train_test_split(all_files, train_size=train_ratio, random_state=42)

    # Create class subdirectories
    train_class_dir = os.path.join(train_dir, class_name)
    val_class_dir = os.path.join(val_dir, class_name)
    os.makedirs(train_class_dir, exist_ok=True)
    os.makedirs(val_class_dir, exist_ok=True)

    # Copy files
    for file_path in train_files:
        shutil.copy2(file_path, train_class_dir)
    for file_path in val_files:
        shutil.copy2(file_path, val_class_dir)

    print(f"[{class_name}] → Train: {len(train_files)}, Val: {len(val_files)}")

print("Dataset cleanup and split completed with random deletion.")



#IMAGE PREPROCESSING FUNCTIONS
#applying clahe to the images for contrast enhancement 
def apply_clahe_to_gray(image, clip_limit=10.0, tile_grid_size=(8, 8)):
    if len(image.shape) == 2:  # grayscale image
      clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
      cl = clahe.apply(image)
      return cl
    else:  # color image
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

# Preprocessing: resize, sharpen, denoise, CLAHE
def preprocess_blurry_image(image, upscale_size=(224, 224), apply_denoise=True):
    #Load the image 
    if image is None:
        raise ValueError("Image not found or path is incorrect.")

    # Resize the image
    image = cv2.resize(image, upscale_size, interpolation=cv2.INTER_CUBIC)

    #Sharpen the image
    blur = cv2.GaussianBlur(image, (5, 5), sigmaX=1)
    sharpened = cv2.addWeighted(image, 1.5, blur, -0.5, 0)

    #Denoise the image
    if apply_denoise:
        denoised = cv2.bilateralFilter(sharpened, d=9, sigmaColor=75, sigmaSpace=75)
    else:
        denoised = sharpened

    enhanced = apply_clahe_to_gray(denoised)
    return enhanced

# Canny edge detection
def apply_canny_edge_detection(image_path, low_thresh=60, high_thresh=130, kernel_size=7):
    #grayscale conversion
    gray = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)

    #Contrast Enhnacement 
    equalized = apply_clahe_to_gray(gray)

    #Noise Reduction 
    blurred = cv2.GaussianBlur(equalized, (kernel_size, kernel_size), 1.4)

    #Gradient Calculation
    grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = cv2.magnitude(grad_x, grad_y)
    gradient_direction = cv2.phase(grad_x, grad_y, angleInDegrees=True)

    #Non-maximum Suppression
    non_max_suppressed = np.zeros_like(gradient_magnitude, dtype=np.uint8)
    angle = gradient_direction / 100.0 * np.pi # To convert to radians

    for i in range(1, gradient_magnitude.shape[0] - 1):
      for j in range(1, gradient_magnitude.shape[1] - 1):
        if (angle[i,j] >=0 and angle[i,j] < np.pi / 4) or (angle[i,j] >= 3* np.pi / 4):
          neighbor1 = gradient_magnitude[i -1, j]
          neighbor2 = gradient_magnitude[i, j + 1]
        else:
              neighbor1 = gradient_magnitude[i - 1, j]
              neighbor2 = gradient_magnitude[i + 1, j]

        if gradient_magnitude[i, j] >= neighbor1 and gradient_magnitude[i, j] >= neighbor2:
            non_max_suppressed[i, j] = gradient_magnitude[i, j]
        else:
            non_max_suppressed[i, j] = 0

    # Double thresholding
    strong_edges = np.zeros_like(non_max_suppressed, dtype=np.uint8)
    weak_edges = np.zeros_like(non_max_suppressed, dtype=np.uint8)
    strong_edges[non_max_suppressed >= high_thresh] = 255
    weak_edges[(non_max_suppressed >= low_thresh) & (non_max_suppressed < high_thresh)] = 100
    
    #Edge tracking by Hysteresis
    edges = np.copy(strong_edges)
    for i in range(1, strong_edges.shape[0] - 1):
        for j in range(1, strong_edges.shape[1] - 1):
            if weak_edges[i, j] == 100:
                if np.any(strong_edges[i - 1:i + 2, j - 1:j + 2] == 255):
                    edges[i, j] = 255
                else:
                    edges[i, j] = 0
    return edges

def compute_sobel_magnitude(edge_img):
    sobelx = cv2.Sobel(edge_img, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(edge_img, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = cv2.magnitude(sobelx, sobely)
    magnitude_image = cv2.convertScaleAbs(magnitude)

    return magnitude_image

# Blend Sobel with base image
def blend_with_sobel(base_img, sobel_map, alpha=0.6, beta=0.4):
    sobel_color = cv2.cvtColor(sobel_map, cv2.COLOR_GRAY2BGR)
    blended = cv2.addWeighted(base_img, alpha, sobel_color, beta, 0)
    blended_image = np.clip(blended, 0, 255).astype(np.uint8)

    return blended_image

# Local Binary Pattern
def compute_lbp(image, P=8, R=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lbp = local_binary_pattern(gray, P, R, method="uniform")
    lbp_normalized = ((lbp - lbp.min()) / (lbp.max() - lbp.min()) * 255).astype(np.uint8)

    return lbp_normalized

# Noise residual to detect subtle differences
def extract_noise_residual(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=40)
    residual = cv2.absdiff(gray, denoised)
    residual_normalized = cv2.normalize(residual, None, 0, 255, cv2.NORM_MINMAX)

    return residual_normalized

# Full pipeline
def full_analysis_pipeline(image, 
                           upscale_size=(224, 224), 
                           apply_denoise=True, 
                           low_thresh=60, 
                           high_thresh=130, 
                           kernel_size=7):

    # Process to enhance the image
    enhanced = preprocess_blurry_image(
        image=image, 
        upscale_size=upscale_size, 
        apply_denoise=apply_denoise
        )
    
    # Edge Detection 
    edges = apply_canny_edge_detection(
        enhanced,
        low_thresh=low_thresh, 
        high_thresh=high_thresh,
        kernel_size=kernel_size
        )

    #Sobel Gradient 
    sobel_map = compute_sobel_magnitude(edges)

    # Blending Enhancec and Sobel Map, overlay 
    blended = blend_with_sobel(enhanced, sobel_map)

    # Local Binary Map for Visualisation 
    lbp_map = compute_lbp(blended)

    # Extracting Residual Noise from image
    residual_normalized = extract_noise_residual(blended)

    # return enhanced, edges, blended, sobel_map, lbp_map, residual_normalized
    
    return blended
