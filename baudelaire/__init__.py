import click
import confuk
import mistune
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from rich.console import Console
from dataclasses import dataclass, field
from typing import *


@dataclass
class Config:
    output_dir: Path
    template_path: Path
    font_path: Path
    title_font_path: Path
    font_size: int = 50
    max_chars_per_line: int = 30
    max_lines: int = 10
    text_color: str = "black"
    text_position: Tuple[int, int | None] = (100, None)
    multiline_spacing: int = 10
    title_position: Tuple[int, int] = (100, 20)
    title_font_size: int = 60
    title_on_all_boards: bool = False
    skip_title: bool = False


def draw_title(config: Config, draw: ImageDraw.Draw, title: str):
    title_x, title_y = config.title_position
    title_font = ImageFont.truetype(str(config.title_font_path), config.title_font_size)
    draw.textbbox((title_x, title_y), title, font=title_font, spacing=config.multiline_spacing)
    draw.text((title_x, title_y), title, fill=config.text_color, font=title_font, spacing=config.multiline_spacing)


def create_instagram_poem_images(poem: str,
                                 title: str | None,
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
        
        # Handle title
        if title is not None and not config.skip_title:
            if not config.title_on_all_boards:
                if i == 0:
                    draw_title(config, draw, title)
            else:
                draw_title(config, draw, title)
        
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


def extract_code_blocks_and_title(markdown_text):
    """Extracts all code blocks from a Markdown string."""
    code_blocks = []
    titles = []

    class CodeBlockExtractor(mistune.HTMLRenderer):
        def block_code(self, code, info=None):
            code_blocks.append(code)
            return super().block_code(code, info)
        def heading(self, text, level, **attrs):
            if level == 1:  # Extract only H1 headings
                titles.append(text)
            return super().heading(text, level, **attrs)

    parser = mistune.create_markdown(renderer=CodeBlockExtractor())
    parser(markdown_text)  # Parses the markdown text

    title = titles[0] if len(titles) > 0 else ""

    return code_blocks, title


def _main(input_: str | Path,
          output_dir: Path,
          title: str | None = None,
          config_path: Path | None = Path):

    if config_path is None:
        try:
            # If running in editable mode:
            config_path = Path(__file__).parent.parent / "config/default.yaml"
        except FileNotFoundError:
            # If running from a built package
            config_path = Path(__file__).parent / "config/default.yaml"

    config = confuk.parse_config(config_path, "omegaconf")
    cfg = Config(
        output_dir,
        **config
    )

    # Handle Markdown files, where codeblocks are assumed to
    # contain the poems:
    if isinstance(input_, Path):
        with open(input_, "r") as f:
            contents = f.read()
        if input_.suffix.lower() == ".md":
            input_str, title = extract_code_blocks_and_title(contents)
            input_str = "\n\n".join(input_str)
        else:
            input_str = contents
    else:
        input_str = input_

    # Call the image-creation fn:
    create_instagram_poem_images(input_str, title, cfg)


@click.command()
@click.argument('input-poem',
                type=str)
@click.option('-o', '--output-dir',
              type=click.Path(exists=False, path_type=Path),
              help="Output directory where image files will be written")
@click.option('-c', '--config-path',
              type=click.Path(exists=True, path_type=Path),
              help="Path to the config file")
@click.option('-f', '--input-is-a-file',
              is_flag=True,
              help="If the input is a file path or text of the poem")
@click.option('-t', '--title',
              type=str,
              help="Poem title, can be left blank")
def main(input_poem, output_dir, config_path, input_is_a_file, title):
    if input_is_a_file:
        input_poem = Path(input_poem)
    _main(input_poem,
          output_dir,
          title,
          config_path or Path(__file__).parent.parent / "config/default.yaml")


if __name__ == "__main__":
    main()
