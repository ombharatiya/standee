# PDF Card Generator

Generates 3" x 7" portrait PDF cards with person images, names, QR codes, and custom messages.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.json` to customize:

- **input_csv**: Path to CSV file with person data (columns: name, image)
- **qr_code_path**: Path to QR code image
- **output_directory**: Where to save generated PDFs
- **message_text**: Custom message text at bottom
- **background_color**: Background color for photo section (hex)
- **Dimensions**: Page and section sizes (in inches)
- **Font sizes**: Name and message font sizes (in points)

## Usage

```bash
# Use default config.json
python generate_cards.py

# Use custom config file
python generate_cards.py my_config.json
```

## Input CSV Format

```csv
name,image
Dr. John Doe,input-sample/images/person1.png
Dr. Jane Smith,input-sample/images/person2.png
```

## Output

PDFs are saved to the output directory with filenames like:
- `dr_john_doe_card.pdf`
- `dr_jane_smith_card.pdf`

Each PDF is exactly 3" x 7" (portrait) at 300 DPI print quality.
