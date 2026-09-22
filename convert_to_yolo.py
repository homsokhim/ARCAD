import json
import shutil
from pathlib import Path


# ==========================================
# Project paths
# ==========================================

root = Path(r"C:\Users\homsokhim\PycharmProjects\Health_analysis")

original_data_root = root / "data" / "stenosis"
yolo_root = root / "data" / "stenosis_yolo"


# ==========================================
# Dataset splits
# ==========================================

splits = ["train", "val", "test"]


# ==========================================
# ARCADE category
# ==========================================

stenosis_categorice = 26

# YOLO class:
# 0 = stenosis


# ==========================================
# Convert one split
# ==========================================

def convert_split(split):

    print()
    print("=" * 50)
    print(f"Processing: {split}")
    print("=" * 50)

    # Original ARCADE paths
    source_image_dir = original_data_root / split / "images"
    annotation_file = (
        original_data_root
        / split
        / "annotations"
        / f"{split}.json"
    )

    # New YOLO paths
    yolo_image = yolo_root / "images" / split
    yolo_label = yolo_root / "labels" / split

    # Create directories
    yolo_image.mkdir(parents=True, exist_ok=True)
    yolo_label.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------
    # Load JSON
    # ------------------------------------------

    with open(annotation_file, "r") as f:
        data = json.load(f)

    images = data["images"]
    annotations = data["annotations"]

    print("Images in JSON:", len(images))
    print("Annotations in JSON:", len(annotations))

    # ------------------------------------------
    # Create annotation dictionary
    # ------------------------------------------

    annotations_by_image = {}

    for ann in annotations:

        # Only stenosis
        if ann["category_id"] != stenosis_categorice:
            continue

        image_id = ann["image_id"]

        if image_id not in annotations_by_image:
            annotations_by_image[image_id] = []

        annotations_by_image[image_id].append(ann)

    # ------------------------------------------
    # Convert images
    # ------------------------------------------

    copied_images = 0
    created_labels = 0

    for image_info in images:

        image_id = image_info["id"]
        file_name = image_info["file_name"]

        width = image_info["width"]
        height = image_info["height"]

        # Original image
        source_image = source_image_dir / file_name

        # New YOLO image
        destination_image = yolo_image / file_name

        # Copy image
        shutil.copy2(
            source_image,
            destination_image
        )

        copied_images += 1

        # --------------------------------------
        # YOLO label filename
        # --------------------------------------

        label_name = Path(file_name).stem + ".txt"

        label_file = yolo_label / label_name

        image_annotations = annotations_by_image.get(
            image_id,
            []
        )

        # --------------------------------------
        # Write YOLO segmentation
        # --------------------------------------

        with open(label_file, "w") as f:

            for ann in image_annotations:

                segmentation = ann.get("segmentation", [])

                for polygon in segmentation:

                    if len(polygon) < 6:
                        continue

                    # YOLO format:
                    # class x1 y1 x2 y2 ...

                    values = ["0"]

                    for i in range(0, len(polygon), 2):

                        x = polygon[i]
                        y = polygon[i + 1]

                        # Normalize coordinates
                        x_norm = x / width
                        y_norm = y / height

                        values.append(str(x_norm))
                        values.append(str(y_norm))

                    f.write(
                        " ".join(values) + "\n"
                    )

        if image_annotations:
            created_labels += 1

    print("Copied images:", copied_images)
    print("Images with stenosis labels:", created_labels)


# ==========================================
# Run conversion
# ==========================================

for split in splits:
    convert_split(split)


print()
print("=" * 50)
print("Conversion finished!!!")
print("=" * 50)