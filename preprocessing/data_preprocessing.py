import numpy as np
import pandas as pd
import cv2
import os
import re 
import hashlib

# Rename the images in the Raw/Images [Generated & Real]
# #Function to extract the numbers from the file name
# def extract_class_name(file_name):
#     # Remove the file extension
#     file_name = os.path.splitext(file_name)[0]

#     # Remove numbers and parentheses
#     file_name = re.sub(r'\(\d+\)', '', file_name)  # Remove patterns like "(1)"
#     # Replace underscores with spaces
#     class_name = file_name.replace('_', ' ').strip()
#     return class_name

# Generated = '../data/raw/Images/Generated'
# Real = '../data/raw/Images/Real'

# data = []

# generated_counter = 1
# real_counter = 1

# # Process Generated images
# for root, dirs, files in os.walk(Generated):
#     for file in sorted(files):
#         if file.lower().endswith('.jpg'):
#             old_path = os.path.join(root, file)
#             new_name = f"generated_{generated_counter}.jpg"
#             new_path = os.path.join(root, new_name)

#             if old_path != new_path and not os.path.exists(new_path):
#                 os.rename(old_path, new_path)
#                 print(f"Renamed: {file} → {new_name}")

#             class_name = extract_class_name(file)
#             data.append({'file_path': new_path, 'class_name': class_name})
#             generated_counter += 1

# # Process Real images
# for root, dirs, files in os.walk(Real):
#     for file in sorted(files):
#         if file.lower().endswith('.jpg'):
#             old_path = os.path.join(root, file)
#             new_name = f"real_{real_counter}.jpg"
#             new_path = os.path.join(root, new_name)

#             if old_path != new_path and not os.path.exists(new_path):
#                 os.rename(old_path, new_path)
#                 print(f"Renamed: {file} → {new_name}")

#             class_name = extract_class_name(file)
#             data.append({'file_path': new_path, 'class_name': class_name})
#             real_counter += 1
            
            
            
# Find Duplicated images in Generated image folder and deletes them. 

# def get_hash(image_path):
#     with open(image_path, 'rb') as f:
#         return hashlib.md5(f.read()).hexdigest()

# def find_duplicates(directory):
#     hashes = {}
#     duplicates = []

#     for filename in os.listdir(directory):
#         if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#             path = os.path.join(directory, filename)
#             file_hash = get_hash(path)

#             if file_hash in hashes:
#                 duplicates.append((path, hashes[file_hash]))  # full paths
#             else:
#                 hashes[file_hash] = path

#     return duplicates

# # Update with your image folder
# image_dir = "../data/raw/Images/Generated"

# dups = find_duplicates(image_dir)

# for dup, original in dups:
#     print(f"Duplicate: {dup} --> Original: {original}")

# # Delete duplicate files (only dup, not original)
# for dup_path, original_path in dups:
#     try:
#         os.remove(dup_path)
#         print(f"Deleted duplicate: {dup_path}")
#     except Exception as e:
#         print(f"Failed to delete {dup_path}: {e}")



# Find Duplicated images in Real image folder and delete them. 

# def get_hash(image_path):
#     with open(image_path, 'rb') as f:
#         return hashlib.md5(f.read()).hexdigest()

# def find_duplicates(directory):
#     hashes = {}
#     duplicates = []

#     for filename in os.listdir(directory):
#         if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
#             path = os.path.join(directory, filename)
#             file_hash = get_hash(path)

#             if file_hash in hashes:
#                 duplicates.append((path, hashes[file_hash]))  # full paths
#             else:
#                 hashes[file_hash] = path

#     return duplicates

# # Real Images folder
# image_dir = "../data/raw/Images/Real"

# dups = find_duplicates(image_dir)

# for dup, original in dups:
#     print(f"Duplicate: {dup} --> Original: {original}")

# # Delete duplicate files (only dup, not original)
# for dup_path, original_path in dups:
#     try:
#         os.remove(dup_path)
#         print(f"Deleted duplicate: {dup_path}")
#     except Exception as e:
#         print(f"Failed to delete {dup_path}: {e}")