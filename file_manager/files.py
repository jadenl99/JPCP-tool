import os
class FileManager:
    def __init__(self, path: str):
        self.path = path

    

    def get_im_id(self, s):
        s = s[::-1]
        start_index = -1
        end_index = -1
        for i, c in enumerate(s):
            if c.isdigit():
                end_index = i + 1
                if start_index == -1:
                    start_index = i
            elif start_index > -1:
                break
        if start_index == -1:
            return None

        return int(s[start_index:end_index][::-1])

    
    def filter_files(self, path, file_type) -> list:
        # Returns files of specified file type
        filtered = list(filter(lambda file: 
                               file.split(".")[-1] == file_type, 
                               os.listdir(path)))
        filtered.sort()
        return filtered
        