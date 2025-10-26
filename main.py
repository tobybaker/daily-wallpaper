import pathlib
import numpy as np

from PIL import Image, ImageDraw
from dataclasses import dataclass
from coloraide import Color

@dataclass
class Circle:
    x: int
    y: int
    radius: int
    color: tuple

class ImageGenerator:
    #CONSTANTS
    IMAGE_WIDTH:int = 1080
    IMAGE_HEIGHT:int = 2400
    BACKGROUND_COLOR:tuple = (240, 240, 240)  # Light gray background

    DEFAULT_MID_RADIUS:float = 100.0
    DEFAULT_BASE_RADIUS:float = 5.0
    RADIUS_VARIANCE = 0.25  
    MAX_CIRCLE_COUNT = 3000
    MAX_PLACEMENT_ATTEMPTS = 10

    def __init__(self, width:int=1080, height:int=2400):
        self.width = width
        self.height = height
        self.RNG = np.random.default_rng()
        

    def get_radius_range(self, generate_index: int, num_circles: int):

        mid_radius:float = self.DEFAULT_MID_RADIUS * (1 - (generate_index / num_circles)) + self.DEFAULT_BASE_RADIUS
        min_radius:int = int(mid_radius * (1 - self.RADIUS_VARIANCE))
        max_radius:int = int(mid_radius * (1 + self.RADIUS_VARIANCE))
        return min_radius, max_radius

    def check_for_overlap_same_color(self,test_circle:Circle,circles:list[Circle]) -> bool:
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
        max_attempts: int = self.MAX_PLACEMENT_ATTEMPTS
        
        for _ in range(num_circles):
            attempts += 1
            x: int = self.RNG.integers(0, self.width)
            y: int = self.RNG.integers(0, self.height)

            min_radius, max_radius = self.get_radius_range(generate_index, num_circles)
            radius: int = int(self.RNG.integers(min_radius, max_radius))
            color: tuple  = color_pallete[self.RNG.integers(0, len(color_pallete))]
            new_circle = Circle(x=x, y=y, radius=radius, color=color)

            if self.check_for_overlap_same_color(new_circle, circles):
                if attempts >= max_attempts:
                    generate_index += 1
                    attempts = 0
                continue
            generate_index += 1
            circles.append(new_circle)
        return circles
    def generate_color_pallete(self,lightness_range:tuple=(0.3,0.7),saturation_range:tuple=(0.4,1.0),n_color_range:tuple=(3,25)) -> list[tuple]:
        num_colors: int = int(self.RNG.integers(*n_color_range))
        colors: list[tuple] = []
        for _ in range(num_colors):
            lightness: float = self.RNG.uniform(*lightness_range)
            saturation: float = self.RNG.uniform(*saturation_range)
            color: Color = Color("hsl", [
                int(self.RNG.integers(0, 360)),
                saturation,
                lightness
            ]).convert("srgb").coords()
            color: tuple = tuple(int(c * 255) for c in color)

            colors.append(color)
        
        return colors
    def create_image(self):
        image = Image.new("RGB", (self.width, self.height), self.BACKGROUND_COLOR)

        color_pallete    = self.generate_color_pallete()
        circle_data = self.generate_circle_data(num_circles=self.MAX_CIRCLE_COUNT,color_pallete=color_pallete)

        draw = ImageDraw.Draw(image)
        for circle in circle_data:
            bbox = [circle.x - circle.radius, circle.y - circle.radius,
                    circle.x + circle.radius, circle.y + circle.radius]
            draw.ellipse(bbox, fill=circle.color, outline=None)
        image
        return image
def main():

    output_dir = pathlib.Path("images/current")

    image_generator = ImageGenerator()
    image: Image.Image = image_generator.create_image()
    output_path = output_dir / "generated_image.png"
    output_dir.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

if __name__ == "__main__":
    main()
