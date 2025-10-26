import pathlib
import numpy as np
from PIL import Image, ImageDraw
#import dataclass

from dataclasses import dataclass
@dataclass
class Circle:
    x: int
    y: int
    radius: int
    color: tuple

class ImageGenerator:
    def __init__(self, width:int=1080, height:int=2400, color:tuple=(0, 128, 255)):
        self.width = width
        self.height = height
        self.color = color

        self.RNG = np.random.default_rng()
        self.image = self.create_image()

    def get_radius_range(self, generate_index: int, num_circles: int):
        
        mid_radius:float = 100.0 * (1 - (generate_index / num_circles))+5.0
        min_radius:int = int(mid_radius * 0.75)
        max_radius:int = int(mid_radius * 1.25)
        return min_radius, max_radius

    def check_for_overlap(self,test_circle:Circle,circles:list[Circle]) -> bool:
        for circle in circles:
            dist_sq: int = (test_circle.x - circle.x) ** 2 + (test_circle.y - circle.y) ** 2
            radius_sum: int = test_circle.radius + circle.radius
            if dist_sq < radius_sum ** 2 and test_circle.color == circle.color:
                return True
        return False

    def generate_circle_data(self, num_circles:int, color_pallete:list[tuple]) -> list[Circle]:
        circles: list[Circle] = []
        generate_index: int =0
        attempts: int =0
        max_attempts: int = 10
        while generate_index < num_circles:
            attempts += 1
            x: int = self.RNG.integers(0, self.width)
            y: int = self.RNG.integers(0, self.height)

            min_radius, max_radius = self.get_radius_range(generate_index, num_circles)
            radius: int = int(self.RNG.integers(min_radius, max_radius))
            color: tuple  = color_pallete[self.RNG.integers(0, len(color_pallete))]
            new_circle = Circle(x=x, y=y, radius=radius, color=color)

            if self.check_for_overlap(new_circle, circles):
                if attempts >= max_attempts:
                    generate_index += 1
                    attempts = 0
                continue
            generate_index += 1
            circles.append(new_circle)
        return circles
    def generate_color_pallete(self, num_colors:int) -> list[tuple]:
        colors: list[tuple] = []
        for _ in range(num_colors):
            color: tuple = tuple(self.RNG.integers(0, 256, size=3))
            colors.append(color)
        return colors
    def create_image(self):
        image = Image.new("RGB", (self.width, self.height), self.color)

        color_pallete    = self.generate_color_pallete(num_colors=10)
        circle_data = self.generate_circle_data(num_circles=3000,color_pallete=color_pallete)
        print(len(circle_data))
        draw = ImageDraw.Draw(image)
        for circle in circle_data:
            bbox = [circle.x - circle.radius, circle.y - circle.radius,
                    circle.x + circle.radius, circle.y + circle.radius]
            draw.ellipse(bbox, fill=circle.color, outline=None)
        image.show()
        return image
def main():

    output_dir = pathlib.Path("images/current")

    image_generator = ImageGenerator()
    output_path = output_dir / "generated_image.png"
    image_generator.image.save(output_path)

if __name__ == "__main__":
    main()
