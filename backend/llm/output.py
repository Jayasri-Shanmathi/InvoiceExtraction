import os
import json
from extraction import extract_invoice

def save_invoice_json(image_path: str, output_folder: str = "output"):
    data = extract_invoice(image_path)
    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Invoice JSON saved at: {output_path}")
    return output_path, data

if __name__ == "__main__":
    save_invoice_json("sample_invoice.png")
