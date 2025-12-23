from flask import Flask, render_template, request
from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"
PLOT_FOLDER = "static/plots"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)


# def save_histogram(image, filename):
#     data = np.array(image)
#     plt.figure()
#     if len(data.shape) == 3:
#         for i, color in enumerate(['r', 'g', 'b']):
#             plt.hist(data[:, :, i].flatten(), bins=256, color=color, alpha=0.5)
#     else:
#         plt.hist(data.flatten(), bins=256)
#     plt.title("Color distribution")
#     plt.savefig(filename)
#     plt.close()

def save_histogram(image, filename):
    data = np.array(image)

    fig = plt.figure()
    try:
        if len(data.shape) == 3:
            for i, color in enumerate(['r', 'g', 'b']):
                plt.hist(
                    data[:, :, i].flatten(),
                    bins=256,
                    color=color,
                    alpha=0.5
                )
        else:
            plt.hist(data.flatten(), bins=256)

        plt.title("Color distribution")
        plt.savefig(filename)
    finally:
        plt.close(fig)



@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    result_images = []
    plots = []

    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            return render_template("index.html")

        uid = str(uuid.uuid4())

        upload_dir = os.path.join(UPLOAD_FOLDER, uid)
        result_dir = os.path.join(RESULT_FOLDER, uid)
        plot_dir = os.path.join(PLOT_FOLDER, uid)

        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(result_dir, exist_ok=True)
        os.makedirs(plot_dir, exist_ok=True)

        img_path = os.path.join(upload_dir, file.filename)
        file.save(img_path)

        with Image.open(img_path) as img:
            img = img.convert("RGB")
            w, h = img.size

            parts = [
                img.crop((0, 0, w // 2, h // 2)),
                img.crop((w // 2, 0, w, h // 2)),
                img.crop((0, h // 2, w // 2, h)),
                img.crop((w // 2, h // 2, w, h)),
            ]

            orig_plot = os.path.join(plot_dir, "original.png")
            save_histogram(img, orig_plot)
            plots.append(orig_plot)

            for i, part in enumerate(parts):
                part_img = os.path.join(result_dir, f"part_{i}.png")
                part_plot = os.path.join(plot_dir, f"plot_{i}.png")

                part.save(part_img)
                save_histogram(part, part_plot)

                result_images.append(part_img)
                plots.append(part_plot)

    return render_template(
        "index.html",
        images=result_images,
        plots=plots
    )


# def index():
#     result_images = []
#     plots = []

#     if request.method == "POST":
#         file = request.files["image"]
#         if file:
#             uid = str(uuid.uuid4())
#             path = os.path.join(UPLOAD_FOLDER, uid + "_" + file.filename)
#             file.save(path)

#             with Image.open(path) as image:
#                 image = image.convert("RGB")
#             w, h = image.size
#             parts = [
#                 image.crop((0, 0, w//2, h//2)),
#                 image.crop((w//2, 0, w, h//2)),
#                 image.crop((0, h//2, w//2, h)),
#                 image.crop((w//2, h//2, w, h)),
#             ]

#             orig_plot = os.path.join(PLOT_FOLDER, f"{uid}_orig.png")
#             save_histogram(image, orig_plot)
#             plots.append(orig_plot)

#             for i, part in enumerate(parts):
#                 img_path = os.path.join(RESULT_FOLDER, f"{uid}_part{i}.png")
#                 plot_path = os.path.join(PLOT_FOLDER, f"{uid}_plot{i}.png")
#                 part.save(img_path)
#                 save_histogram(part, plot_path)
#                 result_images.append(img_path)
#                 plots.append(plot_path)

#     return render_template("index.html",
#                            images=result_images,
#                            plots=plots)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)