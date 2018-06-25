from io import FileIO, SEEK_CUR

from util.io_helper import IOHelper

MPK_MAGIC = 'MPK'
MPK_VERSION = 131072


class MPK:
    def __init__(self, io):
        self._io = io
        self._files = []
        self._version = MPK_VERSION

    @staticmethod
    def load(io: FileIO):
        instance = MPK(io)
        magic = IOHelper.read_ascii_string(io, 4)
        if magic == MPK_MAGIC:
            version, count = IOHelper.read_struct(io, '<2i')
            io.seek(52, SEEK_CUR)
            instance.set_version(version)
            for i in range(count):
                is_zip, index, offset, data_size, zip_size = IOHelper.read_struct(io, '<2i3q')
                name_data = io.read(224)
                name = name_data[:name_data.find(b'\x00')].decode(encoding='ascii')
                instance.insert_file({
                    'is_zip': is_zip != 0,
                    'index': index,
                    'offset': offset,
                    'data_size': data_size,
                    'zip_size': zip_size,
                    'name': name,
                    'data': None,
                })

        return instance

    def set_version(self, version):
        self._version = version

    def insert_file(self, file, index=None):
        i = 0
        if index is None:
            i = len(self._files)
        self._files.insert(i, file)

    def data(self, index):
        if index < len(self._files):
            file = self._files[index]  # type: dict
            if file['data'] is None:
                if not file['is_zip']:
                    data = IOHelper.read_range(self._io, file['offset'], file['data_size'])
                    file['data'] = data
                else:
                    raise Exception('Unsupport File.')
            else:
                data = file['data']

            return data

    def file(self, index):
        if index < len(self._files):
            file = self._files[index].copy()
            file.pop('data')
            return file

    @property
    def files(self):
        return [i for i in range(len(self._files))]
