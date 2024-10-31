import os
import platform
import subprocess
from PIL import Image
from io import BytesIO

def copy_image_to_clipboard(image_path):
    # Load the image
    img = Image.open(image_path)

    if platform.system() == "Windows":
        import win32clipboard  # Import only on Windows
        # For Windows using pywin32
        output = BytesIO()
        img.save(output, 'BMP')
        data = output.getvalue()[14:]  # Remove the BMP header
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    elif platform.system() == "Darwin":
        # For macOS using subprocess
        img.save("/tmp/temp_image.png")  # Save temporarily
        result = subprocess.run(["osascript", "-e", f"set the clipboard to (read (POSIX file \"/tmp/temp_image.png\") as JPEG picture)"], capture_output=True)
        if result.returncode != 0:
            print("Failed to copy to clipboard:", result.stderr.decode())
    elif platform.system() == "Linux":
        # For Linux using xclip
        img.save("/tmp/temp_image.png")  # Save temporarily
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', '/tmp/temp_image.png'], capture_output=True)
        if result.returncode != 0:
            print("Failed to copy to clipboard:", result.stderr.decode())
    else:
        raise OSError("Unsupported operating system.")


def format_file_size(file_size):
    file_size_str = "Size: "
    if (file_size>1048576): # >1MB
        file_size_str += f"{file_size/1048576 :.2f}MB"
    elif (file_size>1024): # >1KB
        file_size_str += f"{file_size/1024 :.2f}KB"
    else:
        file_size_str += f"{file_size :.2f}B"
    return file_size_str
