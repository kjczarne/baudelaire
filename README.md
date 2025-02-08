<p align="center">
  <img src="static/logo.png" alt="logo" width="200" style="display: block;margin-left: auto;margin-right: auto;"/>
</p>
</br>

<p align="center">
Create Instagram posts from your plaintext poetry in seconds:
</p>

</br>
<p align="center">
<img src="static/poem_part_1.png" alt="logo" width="300" style="display: block;margin-left: auto;margin-right: auto;"/>
</p>

</br>

## Installation

```bash
pip install baudelaire
```

## Usage

```bash
baudelaire "<plaintext-input>" -o "<output-directory>" -c "<config>"
```

For example:

```bash
baudelaire -o "outputs" "$(cat "poem.txt")"
```

> [!note]
> The input is expected to be a plaintext poem, so you can write the contents directly in the command line or `cat` them from a plaintext file.

The text will be written to the specified output directory as `poem_part-*.png` files. There is a default configuration file which is distributed as a part of the package.

You can give it a try by using Dylan Thomas' _Do not go gentle into that good night_:

```bash
baudelaire -o "outputs" "$(cat "tests/rage.txt")"
```

## Configuration

The default config is available in the repository under `config/default.yaml`. Check out the comments to understand what each configuration option does.

> [!note]
> If you change the font you might need to tweak other parameters like the number of lines per board. It's recommended to create a separate config per template.
