
def format_file_size(file_size):
    file_size_str = "Size: "
    if (file_size>1048576): # >1MB
        file_size_str += f"{file_size/1048576 :.2f}MB"
    elif (file_size>1024): # >1KB
        file_size_str += f"{file_size/1024 :.2f}KB"
    else:
        file_size_str += f"{file_size :.2f}B"
    return file_size_str
