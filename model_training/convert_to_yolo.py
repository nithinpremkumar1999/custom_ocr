import os
import cv2
import json
import shutil
import argparse


def move_png(data, png_folder, output_folder):
  """
  """
  image_info = {}

  for i in data["images"]:
    png_file = os.path.join(png_folder, i["file_name"])
    img = cv2.imread(png_file)
    img = cv2.resize(img, (640, 640))
    cv2.imwrite(png_file, img)
    png_destination = os.path.join(output_folder, i["file_name"])
    # move the png_file
    try:
      shutil.move(png_file, png_destination)
      image_info[i["file_name"]] = {"width": i["width"],\
      "height": i["height"],\
      "id": i["id"]}
    except Exception as e:
      raise e

  return image_info


def get_annotations(data, img_id):
  """
  """
  img_ann = []
  is_annotated = False
  
  for ann in data["annotations"]:
    if ann["image_id"] == img_id:
      img_ann.append(ann)
      is_annotated = True

  if is_annotated:
    return img_ann
  else:
    return None


def move_labels(data, image_info, output_folder):
  """
  """
  for image, info in image_info.items():
    img_id = info["id"]
    img_height = info["height"]
    img_width = info["width"]
    
    # get annotations
    img_ann = get_annotations(data, img_id)
    if img_ann:
      txt_name = image.split(".")[0]
      txt_name += ".txt"
      label_file = open(os.path.join(output_folder, txt_name), "a")

      for ann in img_ann:
        category_id = ann["category_id"]
        bbox = ann["bbox"]
        x, y, w, h = bbox

        # find midpoints
        x_center, y_center = (x+(x+w)) / 2, (y+(y+h)) / 2

        #normalizations
        x_center, y_center = x_center / img_width, y_center / img_height
        w, h = w / img_width, h / img_height

        # limiting upto fix number of decimal places
        x_center, y_center = format(x_center, '.6f'), format(y_center, '.6f')
        w, h = format(w, '.6f'), format(h, '.6f')

        # write to current file
        label_file.write(f"{category_id} {x_center} {y_center} {w} {h}\n")

      label_file.close()


def convert(json_file, png_folder, output_folder):
  """
  """
  with open(json_file) as f:
    data = json.load(f)
  
  try:
    os.mkdir(os.path.join(output_folder, 'images'))
    os.mkdir(os.path.join(output_folder, 'labels'))
  except Exception as e:
    pass

  # move to <output_folder>/images
  image_info = move_png(data, png_folder, os.path.join(output_folder, 'images'))
  # move to <output_folder>/labels
  move_labels(data, image_info, os.path.join(output_folder, 'labels'))


parser = argparse.ArgumentParser(description ='Convert COCO json to YOLO format')
parser.add_argument('json_file', metavar ='j', 
                    type = str,
                    help ='path to json file')
parser.add_argument('png_folder', metavar ='p', 
                    type = str,
                    help ='path to png folder')
parser.add_argument('output_folder', metavar ='o', 
                    type = str,
                    help ='path to output_folder')

args = parser.parse_args()
convert(args.json_file, args.png_folder, args.output_folder)



