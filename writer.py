import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"obj"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def list_obj_files():
    files = os.listdir(UPLOAD_FOLDER)
    return [file for file in files if file.endswith(".obj")]


@app.route("/")
def upload_form():
    obj_files = list_obj_files()
    obj_files = ["wall", "plane", "sauron"] + obj_files
    return render_template_string(
        """
    <!doctype html>
    <html>
        <head>
            <title>Volumetric Display</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <script>
                function toggleRotationOptions() {
                    const selectedFile = document.getElementById("selected_file").value;
                    const rotationOptions = document.getElementById("rotation_options");
                    if (selectedFile.endsWith(".obj")) {
                        rotationOptions.style.display = "block";
                    } else {
                        rotationOptions.style.display = "none";
                    }
                }
            </script>
        </head>
        <body class="bg-gray-100 text-gray-800">
            <div class="container mx-auto p-6">
                <h1 class="text-2xl font-bold mb-4">Select an Effect</h1>
                <form action="/select" method="POST" class="bg-white p-6 rounded-lg shadow-lg">
                    <label for="selected_file" class="block mb-2 text-sm font-medium text-gray-700">Choose a file:</label>
                    <select id="selected_file" name="selected_file" class="block w-full p-2 border border-gray-300 rounded-lg mb-4" onchange="toggleRotationOptions()">
                        {% for file in obj_files %}
                            <option value="{{ file }}">{{ file }}</option>
                        {% endfor %}
                    </select>
                    
                    <div id="rotation_options" style="display: none;" class="mt-4">
                        <h2 class="text-lg font-semibold mb-2">Choose Rotation Axis</h2>
                        <div class="mb-4">
                            <label class="inline-flex items-center">
                                <input type="radio" id="x" name="rotation_axis" value="X" class="form-radio" checked>
                                <span class="ml-2">X</span>
                            </label>
                            <label class="inline-flex items-center ml-4">
                                <input type="radio" id="y" name="rotation_axis" value="Y" class="form-radio">
                                <span class="ml-2">Y</span>
                            </label>
                            <label class="inline-flex items-center ml-4">
                                <input type="radio" id="z" name="rotation_axis" value="Z" class="form-radio">
                                <span class="ml-2">Z</span>
                            </label>
                        </div>
                        <label for="rotation_speed" class="block text-sm font-medium text-gray-700">Rotation Speed:</label>
                        <input type="number" id="rotation_speed" name="rotation_speed" class="block w-full p-2 border border-gray-300 rounded-lg" min="0" max="100" value="0">
                    </div>
                    
                    <button type="submit" class="mt-6 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Submit</button>
                </form>

                <h2 class="text-xl font-bold mt-8 mb-4">Upload an Effect</h2>
                <form action="/upload" method="POST" enctype="multipart/form-data" class="bg-white p-6 rounded-lg shadow-lg">
                    <label for="file" class="block mb-2 text-sm font-medium text-gray-700">Upload a .obj file:</label>
                    <input type="file" name="file" accept=".obj" class="block w-full mb-4 p-2 border border-gray-300 rounded-lg">
                    <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600">Upload</button>
                </form>
            </div>
        </body>
    </html>
    """,
        obj_files=obj_files,
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file or file.filename == "":
        return render_template_string(
            """
        <!doctype html>
        <html>
            <head>
                <title>Upload Error</title>
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            </head>
            <body class="bg-gray-100 text-gray-800">
                <div class="container mx-auto p-6">
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h1 class="text-2xl font-bold text-red-600">No file uploaded</h1>
                        <a href="/" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Try again</a>
                    </div>
                </div>
            </body>
        </html>
        """
        )

    if not allowed_file(file.filename):
        return render_template_string(
            """
        <!doctype html>
        <html>
            <head>
                <title>Upload Error</title>
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            </head>
            <body class="bg-gray-100 text-gray-800">
                <div class="container mx-auto p-6">
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h1 class="text-2xl font-bold text-red-600">Invalid file type. Only .obj files are allowed.</h1>
                        <a href="/" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Try again</a>
                    </div>
                </div>
            </body>
        </html>
        """
        )

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    return render_template_string(
        """
    <!doctype html>
    <html>
        <head>
            <title>Upload Success</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body class="bg-gray-100 text-gray-800">
            <div class="container mx-auto p-6">
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    <h1 class="text-2xl font-bold text-green-600">File "{{ file }}" uploaded successfully!</h1>
                    <a href="/" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Back</a>
                </div>
            </div>
        </body>
    </html>
    """,
        file=file.filename,
    )


@app.route("/select", methods=["POST"])
def select_file():
    selected_file = request.form.get("selected_file")
    rotation_axis = request.form.get("rotation_axis")
    rotation_speed = request.form.get("rotation_speed")

    if selected_file and selected_file.endswith(".obj"):
        if rotation_axis and rotation_speed:
            queue.put(
                {"file": selected_file, "axis": rotation_axis, "speed": rotation_speed}
            )
            return render_template_string(
                """
            <!doctype html>
            <html>
                <head>
                    <title>Selection Success</title>
                    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
                </head>
                <body class="bg-gray-100 text-gray-800">
                    <div class="container mx-auto p-6">
                        <div class="bg-white p-6 rounded-lg shadow-lg">
                            <h1 class="text-2xl font-bold text-green-600">You selected:</h1>
                            <p class="mt-2">File: <span class="font-semibold">{{ file }}</span></p>
                            <p>Rotation Axis: <span class="font-semibold">{{ axis }}</span></p>
                            <p>Rotation Speed: <span class="font-semibold">{{ speed }}</span></p>
                            <a href="/" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Back</a>
                        </div>
                    </div>
                </body>
            </html>
                """,
                file=selected_file,
                axis=rotation_axis,
                speed=rotation_speed,
            )

    elif selected_file:
        queue.put({"file": selected_file, "axis": None, "speed": None})
        return render_template_string(
            """
        <!doctype html>
        <html>
            <head>
                <title>Selection Success</title>
                <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            </head>
            <body class="bg-gray-100 text-gray-800">
                <div class="container mx-auto p-6">
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h1 class="text-2xl font-bold text-green-600">You selected:</h1>
                        <p class="mt-2">File: <span class="font-semibold">{{ file }}</span></p>
                        <a href="/" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Back</a>
                    </div>
                </div>
            </body>
        </html>
            """,
            file=selected_file,
        )

    return render_template_string(
        """
    <!doctype html>
    <html>
        <head>
            <title>Selection Error</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body class="bg-gray-100 text-gray-800">
            <div class="container mx-auto p-6">
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    <h1 class="text-2xl font-bold text-red-600">Invalid selection. Please try again.</h1>
                    <a href="/" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Back</a>
                </div>
            </div>
        </body>
    </html>
    """
    )


def run_writer(q):
    global queue
    queue = q
    app.run(host="0.0.0.0", port=5000)
