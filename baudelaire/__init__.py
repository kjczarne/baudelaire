import click
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
    text_position: Tuple[int, int | None] = (100, None)
    multiline_spacing: int = 10


def create_instagram_poem_images(poem: str,
                                 config: Config):
    console = Console()
    os.makedirs(config.output_dir, exist_ok=True)

    # Preserve line breaks while wrapping text
    lines = []
    for paragraph in poem.split("\n"):
        if "<break>" in paragraph:
            lines.append("<break>")
        else:
            lines.extend(textwrap.wrap(paragraph, width=config.max_chars_per_line) if paragraph else [""])
    
    # Split text into chunks, respecting explicit breaks
    chunks = []
    chunk = []
    for line in lines:
        if line == "<break>" or len(chunk) >= config.max_lines:
            if chunk:
                chunks.append("\n".join(chunk))
                chunk = []
        if line != "<break>":
            chunk.append(line)
    if chunk:
        chunks.append("\n".join(chunk))
    
    images = []
    for i, chunk in enumerate(chunks):
        # Load template
        img = Image.open(config.template_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(str(config.font_path), config.font_size)
        
        # Define text position (centrally aligned vertically)
        text_x, maybe_text_y = config.text_position
        _, img_height = img.size
        text_bbox = draw.textbbox((0, 0), chunk, font=font, spacing=config.multiline_spacing)
        text_height = text_bbox[3] - text_bbox[1]  # Height is (bottom - top)

        if maybe_text_y is not None:
            text_y = maybe_text_y  # Explicit position
        else:
            text_y = (img_height - text_height) // 2  # Center vertically

        # Draw text
        draw.multiline_text((text_x, text_y), chunk, fill=config.text_color, font=font, spacing=config.multiline_spacing)
        
        # Save output
        output_path = config.output_dir / f"poem_part_{i + 1}.png"
        img.save(output_path)
        images.append(str(output_path))

    console.print(f"Saved {len(images)} images in {config.output_dir}")
    return images


def _main(input_: str,
          output_dir: Path,
          config_path: Path = Path(__file__).parent.parent / "config/default.yaml"):

    config = confuk.parse_config(config_path, "omegaconf")
    cfg = Config(
        output_dir,
        **config
    )
    create_instagram_poem_images(input_, cfg)


@click.command()
@click.argument('input-poem',
                type=str)
@click.option('-o', '--output-dir',
              type=click.Path(exists=False, path_type=Path),
              help="Output directory where image files will be written")
@click.option('-c', '--config-path',
              type=click.Path(exists=True, path_type=Path),
              help="Path to the config file")
def main(input_poem, output_dir, config_path):
    _main(input_poem, output_dir, config_path or Path(__file__).parent.parent / "config/default.yaml")


if __name__ == "__main__":
    main()
