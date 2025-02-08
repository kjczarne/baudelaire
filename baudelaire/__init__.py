import confuk
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from rich.console import Console
import textwrap
import os
from dataclasses import dataclass, field
from typing import *


@dataclass
class Config:
    output_dir: Path
    template_path: Path
    font_path: Path
    font_size: int = 50
    max_chars_per_line: int = 30
    max_lines: int = 10
    text_color: str = "black"
    text_position: Tuple[int, int] = (100, 100)


def create_instagram_poem_images(poem: str,
                                 config: Config):
    console = Console()
    os.makedirs(config.output_dir, exist_ok=True)
    
    # Preserve line breaks while wrapping text:
    lines = []
    for paragraph in poem.split("\n"):
        lines.extend(textwrap.wrap(paragraph,
                                   width=config.max_chars_per_line) if paragraph else [""])
    
    # Split text into chunks based on the number of lines
    # allowed in one image:
    chunks = ["\n".join(lines[i : i + config.max_lines])
              for i in range(0, len(lines), config.max_lines)]

    images = []
    for i, chunk in enumerate(chunks):
        # Load template:
        img = Image.open(str(config.template_path)).convert("RGBA")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(config.font_path, config.font_size)
        
        # Define text position (centered):
        text_x, text_y = config.text_position
        
        # Draw text:
        draw.multiline_text((text_x, text_y),
                  chunk,
                  fill=config.text_color,
                  font=font,
                  spacing=10)
        
        # Save output:
        output_path = config.output_dir / f"poem_part_{i + 1}.png"
        img.save(str(output_path))
        images.append(output_path)
    
    console.print(f"Saved {len(images)} images in {config.output_dir}")
    return images


@confuk.main(config=Path(__file__).parent.parent / "config/default.yaml",
             config_format="omegaconf")
def main(config: Config):

    cfg = Config(
        Path(config.output_dir),
        Path(config.template_path),
        Path(config.font_path),
        config.font_size,
        config.max_chars_per_line,
        config.max_lines,
        config.text_color,
        config.text_position
    )

    # Sample poem (Dylan Thomas)
    poem = """
    Do not go gentle into that good night,
    Old age should burn and rave at close of day;
    Rage, rage against the dying of the light.

    Though wise men at their end know dark is right,
    Because their words had forked no lightning they
    Do not go gentle into that good night.

    Good men, the last wave by, crying how bright
    Their frail deeds might have danced in a green bay,
    Rage, rage against the dying of the light.

    Wild men who caught and sang the sun in flight,
    And learn, too late, they grieved it on its way,
    Do not go gentle into that good night.

    Grave men, near death, who see with blinding sight
    Blind eyes could blaze like meteors and
    be gay,
    Rage, rage against the dying of the light.

    And you, my father, there on the sad height,
    Curse, bless, me now with your fierce tears, I pray.
    Do not go gentle into that good night.
    Rage, rage against the dying of the light.
    """
    create_instagram_poem_images(poem, cfg)


if __name__ == "__main__":
    main()
