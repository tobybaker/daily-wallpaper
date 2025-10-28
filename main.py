import pathlib
import numpy as np
import requests
from PIL import Image, ImageDraw
from dataclasses import dataclass
from coloraide import Color
from hashlib import md5


@dataclass
class Circle:
    """
    Represents a circle with position, size, and color.

    Attributes:
        x: X-coordinate of the circle's center
        y: Y-coordinate of the circle's center
        radius: Radius of the circle in pixels
        color: RGB color tuple (r, g, b) with values 0-255
    """

    x: int
    y: int
    radius: int
    color: tuple

    def __repr__(self):
        return (
            f"Circle(x={self.x}, y={self.y}, radius={self.radius}, color={self.color})"
        )


@dataclass
class ImageConfig:
    """
    Configuration settings for image generation.

    Attributes:
        width: Width of the generated image in pixels
        height: Height of the generated image in pixels
        background_color: RGB background color tuple (r, g, b)
    """

    width: int = 1080
    height: int = 2400
    background_color: tuple = (240, 240, 240)  # Light gray

    def __repr__(self):
        return (
            f"ImageConfig(width={self.width}, height={self.height}, "
            f"background_color={self.background_color})"
        )


@dataclass
class ColorPalette:
    colors: list[tuple]
    weights: list[float]


class SeedGenerator:
    # uses requests to get random seed from md5 of bbc
    SEED_IMG_URL: str = "https://www.bbc.co.uk/news"

    def fetch_random_seed(self) -> int:
        try:
            return self.fetch_seed_from_web()
        except requests.RequestException:
            return self.fetch_seed_backup()

    def fetch_seed_from_web(self) -> int:
        response = requests.get(self.SEED_IMG_URL)
        response.raise_for_status()

        content_hash = md5(response.content).hexdigest()
        
        return int(content_hash, 16) % np.iinfo(np.uint32).max

    def fetch_seed_backup(self) -> int:
        return int(np.random.SeedSequence().entropy) % np.iinfo(np.uint32).max


class ColorPaletteGenerator:
    MIN_COLORS: int = 4
    MAX_COLORS: int = 10

    MIN_LIGHTNESS: float = 0.4
    MAX_LIGHTNESS: float = 0.6
    MIN_SATURATION: float = 0.4
    MAX_SATURATION: float = 1.0

    def __init__(self, rng):
        self.rng = rng

    def generate_weights(self, num_colors: int) -> list[float]:
        """Generates a list of weights for the colors in the palette.
        Sampling on simplex"""
        weights = self.rng.normal(size=num_colors)
        weights = np.power(weights, 2)
        weights /= np.sum(weights)
        return weights.tolist()

    def generate(self) -> ColorPalette:
        num_colors: int = int(self.rng.integers(self.MIN_COLORS, self.MAX_COLORS))
        colors: list[tuple] = []

        for _ in range(num_colors):
            lightness: float = self.rng.uniform(self.MIN_LIGHTNESS, self.MAX_LIGHTNESS)
            saturation: float = self.rng.uniform(
                self.MIN_SATURATION, self.MAX_SATURATION
            )
            hsl_color: Color = Color(
                "hsl", [self.rng.uniform(0.0, 360.0), saturation, lightness]
            )

            rgb_coords = hsl_color.convert("srgb").coords()
            rgb_tuple = tuple(int(c * 255) for c in rgb_coords)
            colors.append(rgb_tuple)
        weights = self.generate_weights(num_colors)
        color_palette = ColorPalette(colors=colors, weights=weights)

        return color_palette


class ArtworkGenerator:
    def __init__(self):
        seed = SeedGenerator().fetch_random_seed()
        self.rng = np.random.default_rng(seed)

        self.config = ImageConfig()  # New config class

    def generate(self) -> Image.Image:
        palette = ColorPaletteGenerator(self.rng).generate()
        circles = CircleGenerator(self.rng, self.config).generate(palette)
        return ImageRenderer(self.config).render(circles)


class ImageRenderer:
    def __init__(self, config):
        self.config = config

    def render(self, circles: list[Circle]) -> Image.Image:
        image = Image.new(
            "RGB", (self.config.width, self.config.height), self.config.background_color
        )
        draw = ImageDraw.Draw(image)

        for circle in circles:
            bbox = [
                circle.x - circle.radius,
                circle.y - circle.radius,
                circle.x + circle.radius,
                circle.y + circle.radius,
            ]
            draw.ellipse(bbox, fill=circle.color, outline=None)

        return image


class CircleGenerator:
    DEFAULT_MID_RADIUS: float = 80.0
    DEFAULT_BASE_RADIUS: float = 3.0
    VARIANCE_RADIUS = 0.4
    MAX_CIRCLE_COUNT = 3000
    MAX_PLACEMENT_ATTEMPTS = 1000

    def __init__(self, rng: np.random.Generator, config: ImageConfig):
        self.RNG = rng
        self.config = config

    def get_radius_range(self, generate_index: int) -> tuple[int, int]:
        mid_radius: float = (
            self.DEFAULT_MID_RADIUS * (1 - (generate_index / self.MAX_CIRCLE_COUNT))
            + self.DEFAULT_BASE_RADIUS
        )
        min_radius: int = int(mid_radius * (1 - self.VARIANCE_RADIUS))
        max_radius: int = int(mid_radius * (1 + self.VARIANCE_RADIUS))
        return min_radius, max_radius

    def check_for_overlap_same_color(
        self, test_circle: Circle, circles: list[Circle]
    ) -> bool:
        for circle in circles:
            if test_circle.color != circle.color:
                continue
            distance_squared: int = (test_circle.x - circle.x) ** 2 + (
                test_circle.y - circle.y
            ) ** 2
            radius_sum: int = test_circle.radius + circle.radius
            if distance_squared < radius_sum**2:
                return True
        return False

    def get_new_circle(
        self, generate_index: int, color_palette: ColorPalette
    ) -> Circle:
        min_radius, max_radius = self.get_radius_range(generate_index)
        radius: int = int(self.RNG.integers(min_radius, max_radius))
        x: int = int(self.RNG.integers(0, self.config.width))
        y: int = int(self.RNG.integers(0, self.config.height))

        
        color_index = self.RNG.choice(
            len(color_palette.colors), p=color_palette.weights
        )
        color = color_palette.colors[color_index]
        return Circle(x=x, y=y, radius=radius, color=color)

    def _try_place_circle(
        self, generate_index: int, circles: list[Circle], color_palette: ColorPalette
    ) -> Circle | None:
        placement_attempts: int = 0
        while placement_attempts < self.MAX_PLACEMENT_ATTEMPTS:
            new_circle = self.get_new_circle(generate_index, color_palette)
            placement_attempts += 1
            if not self.check_for_overlap_same_color(new_circle, circles):
                return new_circle
        return None

    def generate(self, color_palette: ColorPalette) -> list[Circle]:
        circles: list[Circle] = []
        for generate_index in range(self.MAX_CIRCLE_COUNT):
            placed_circle = self._try_place_circle(
                generate_index, circles, color_palette=color_palette
            )
            if placed_circle:
                circles.append(placed_circle)
        return circles


def main():
    output_dir = pathlib.Path("images/current")

    image_generator = ArtworkGenerator()
    image: Image.Image = image_generator.generate()
    output_path = output_dir / "daily_generated_wallpaper.png"
    output_dir.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


if __name__ == "__main__":
    main()
