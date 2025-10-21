from socket import INADDR_MAX_LOCAL_GROUP
import easyocr
import cv2
from thefuzz import fuzz
import rtree
from rtree import index
from torch import index_reduce

p = index.Property()
idx_s = index.Index(properties=p)
idx_r = index.Index(properties=p)
idx_l = index.Index(properties=p)
box_data_s = {}
box_data_r = {}
box_data_l = {}

#imagepath = '../examples/2white christmas.png'
#imagepath = "../examples/butternut.jpg"
imagepath = '../examples/GreyGoose.jpg'
rotleft = 'rotleft.jpg'
rotright= 'rotright.jpg'


image = cv2.imread(imagepath)
height, width = image.shape[:2]
print(f"Image size: {width}x{height}")

reader = easyocr.Reader(['en'])
result = reader.readtext(imagepath)
bid_counter = 0
for (bbox, text, prob) in result:
    print(f"Detected text: {text} (Confidence: {prob:.2f}):  bounding box {bbox}")
    
    minx = bbox[0][0]
    miny = bbox[0][1]
    maxx = bbox[2][0]
    maxy = bbox[2][1]
    
    rtreecords = (minx, miny, maxx, maxy)
    idx_s.insert(bid_counter, rtreecords)
    box_data_s[bid_counter] = (bbox, text, prob)
    bid_counter += 1


# s_string = "Samuel Adams"
# tboxes = []
# token = s_string.split()[0]

# for (bbox, text, prob) in result:
#     if fuzz.ratio(s_string.lower(), text.lower()) > 65:
#         tboxes.append(bbox)
#         print(f"  Matched with box: {text}")
    
# image = cv2.imread(imagepath)
# image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
# cv2.imwrite(rotleft, image)
# # result = reader.readtext(rotleft)
# # print("\nRotated Left 90 degrees:\n")
# # for (bbox, text, prob) in result:
# #     print(f"Detected text: {text} (Confidence: {prob:.2f}):  bounding box {bbox}")


    
# image = cv2.imread(imagepath)
# image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
# cv2.imwrite(rotright, image)


# print("\nRotated Right 90 degrees:\n")
# result = reader.readtext(rotright)
# for (bbox, text, prob) in result:
#     print(f"Detected text: {text} (Confidence: {prob:.2f}):  bounding box {bbox}")
    



# # #draw bounding boxes
# # import cv2
# # import numpy as np
# # image = cv2.imread(imagepath)
# # for (bbox, text, prob) in result:
# #     (top_left, top_right, bottom_right, bottom_left) = bbox
# #     top_left = (int(top_left[0]), int(top_left[1]))
# #     top_right = (int(top_right[0]), int(top_right[1]))
# #     bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
# #     bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
    
# #     cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
# #     cv2.putText(image, text, (top_left[0], top_left[1] - 10), 
# #                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
# # cv2.imwrite(imagepath+'_output.jpg', image)


