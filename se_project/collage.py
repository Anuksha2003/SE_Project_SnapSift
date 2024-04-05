import os
from typing import List, Tuple

from PIL import Image


def find_multiples(number : int):
    multiples = set()
    for i in range(number - 1, 1, -1):
        mod = number % i
        if mod == 0:
            tup = (i, int(number / i))
            if tup not in multiples and (tup[1], tup[0]) not in multiples:
                multiples.add(tup)
                
    if len(multiples) == 0:
        mod = number % 2
        div = number // 2
        multiples.add((2, div + mod))
        
    return list(multiples)

def get_smallest_multiples(number : int, smallest_first = True) -> Tuple[int, int]:
    multiples = find_multiples(number)
    smallest_sum = number
    index = 0
    for i, m in enumerate(multiples):
        sum = m[0] + m[1]
        if sum < smallest_sum:
            smallest_sum = sum
            index = i
            
    result = list(multiples[i])
    if smallest_first:
        result.sort()
        
    return result[0], result[1]
    

def create_collage(listofimages : List[str], n_cols : int = 0, n_rows: int = 0, 
                   thumbnail_scale : float = 1.0, thumbnail_width : int = 0, thumbnail_height : int = 0):
    
    n_cols = n_cols if n_cols >= 0 else abs(n_cols)
    n_rows = n_rows if n_rows >= 0 else abs(n_rows)
    
    if n_cols == 0 and n_rows != 0:
        n_cols = len(listofimages) // n_rows
        
    if n_rows == 0 and n_cols != 0:
        n_rows = len(listofimages) // n_cols
        
    if n_rows == 0 and n_cols == 0:
        n_cols, n_rows = get_smallest_multiples(len(listofimages))
    
    thumbnail_width = 0 if thumbnail_width == 0 or n_cols == 0 else round(thumbnail_width / n_cols)
    thumbnail_height = 0 if thumbnail_height == 0 or n_rows == 0 else round(thumbnail_height/n_rows)
    
    all_thumbnails : List[Image.Image] = []
    for p in listofimages:
        thumbnail = Image.open(p)
        if thumbnail_width * thumbnail_scale < thumbnail.width:
            thumbnail_width = round(thumbnail.width * thumbnail_scale)
        if thumbnail_height * thumbnail_scale < thumbnail.height:
            thumbnail_height = round(thumbnail.height * thumbnail_scale)
        
        thumbnail.thumbnail((thumbnail_width, thumbnail_height))
        all_thumbnails.append(thumbnail)

    new_im = Image.new('RGB', (thumbnail_width * n_cols, thumbnail_height * n_rows), 'white')
    
    i, x, y = 0, 0, 0
    for col in range(n_cols):
        for row in range(n_rows):
            if i > len(all_thumbnails) - 1:
                continue
            
            print(i, x, y)
            new_im.paste(all_thumbnails[i], (x, y))
            i += 1
            y += thumbnail_height
        x += thumbnail_width
        y = 0

    extension = os.path.splitext(listofimages[0])[1]
    if extension == "":
        extension = ".jpg"
    destination_file = os.path.join(os.path.dirname(listofimages[0]), f"Collage{extension}")
    new_im.save(destination_file)

list_of_images = ['collection/Anuksha/anuksha2.jpeg','collection/Anuksha/WhatsApp_Image_2024-04-05_at_2.17.47_PM.jpeg']
create_collage(list_of_images)