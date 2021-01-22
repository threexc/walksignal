import csv

def read_csv(data_file):
      with open(data_file) as csv_file:
          data = list(csv.reader(csv_file, delimiter=","))
          csv_file.close()
      return data

def get_bbox(bbox_path):
      bbox = None
      with open(bbox_path) as f:
          bbox = [tuple(map(float, i.split(','))) for i in f]
      return bbox

