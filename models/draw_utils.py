import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from models.access_db_parser import Part


def draw_parts_on_image(image: np.ndarray, parts: List[Part]):
    def scale_dim_to_pixels(real_in_pixels: int, real_in_inches: float, current_in_inches: float) -> int:
        return int(real_in_pixels * (current_in_inches / real_in_inches))

    image_height_pixels, image_width_pixels = image.shape[:2]
    # now we need to scale the diminutions of the part to the image
    real_height_in, real_width_in = 24, 70  # in inches
    for part in parts:
        part_height, part_width = part.get_outer_dims()
        print(f'Part width: {part_width}, Part height: {part_height}')
        part_height_pixels = scale_dim_to_pixels(image_height_pixels, real_height_in, part_height)
        part_width_pixels = scale_dim_to_pixels(image_width_pixels, real_width_in, part_width)
        # now we have to draw a rectangle that represents the part on the image
        if part_height_pixels > part_width_pixels:
            print("rotate part")
        cv2.rectangle(image, (0, 0), (part_width_pixels, part_height_pixels), (0, 255, 0), 4) #changed to dark blue, higher line
        # now we have to draw the outlines of the part on the image
        if part.shaped:
            outlines = part.get_outlines()
            for pt1, pt2 in outlines:
                pt1 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt1[0]),
                       scale_dim_to_pixels(image_height_pixels, real_height_in, pt1[1]))
                pt2 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt2[0]),
                       scale_dim_to_pixels(image_height_pixels, real_height_in, pt2[1]))
                cv2.line(image, pt1, pt2, (0, 255, 0), 3)
        # now we have to draw the operations of the part on the image
        for operation in part.operations:
            op_height, op_width = operation.get_outer_dims()
            op_height_pixels = scale_dim_to_pixels(image_height_pixels, real_height_in, op_height)
            op_width_pixels = scale_dim_to_pixels(image_width_pixels, real_width_in, op_width)
            # now we have to draw a rectangle that represents the operation on the image
            xpos, ypos = operation.get_init_pos()
            xpos_pixels = scale_dim_to_pixels(image_width_pixels, real_width_in, xpos)
            ypos_pixels = scale_dim_to_pixels(image_height_pixels, real_height_in, ypos)
            cv2.rectangle(image, (xpos_pixels, ypos_pixels), (xpos_pixels + op_width_pixels, ypos_pixels + op_height_pixels),
                          (0, 255, 255), 2)
            # now we have to draw the outlines of the operation on the image
            outlines = operation.get_outlines()
            for pt1, pt2 in outlines:
                pt1 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt1[0]),
                       scale_dim_to_pixels(image_height_pixels, real_height_in, pt1[1]))
                pt2 = (scale_dim_to_pixels(image_width_pixels, real_width_in, pt2[0]),
                       scale_dim_to_pixels(image_height_pixels, real_height_in, pt2[1]))
                cv2.line(image, pt1, pt2, (0, 255, 0), 3)
    image = cv2.flip(image, 0)
    return image



