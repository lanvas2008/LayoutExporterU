from collections import OrderedDict
import struct
import xmltodict


def xmlToDict(file, process_namespaces=False, namespaces={}):
    with open(file) as inf:
        xml = inf.read()

    return xmltodict.parse(xml, process_namespaces=process_namespaces, namespaces=namespaces)


def dictToXml(dict_, pretty=True):
    return xmltodict.unparse(dict_, pretty=pretty)


def readString(data, offset=0, charWidth=1, encoding='utf-8'):
    end = data.find(b'\0' * charWidth, offset)
    if end == -1:
        return data[offset:].decode(encoding)

    return data[offset:end].decode(encoding)


def roundUp(x, y):
    return ((x - 1) | (y - 1)) + 1


class BlockHeader:
    def __init__(self, file, pos):
        self.magic, self.size = struct.unpack_from('>4sI', file, pos)

    def save(self):
        return struct.pack(
            '>4sI',
            self.magic,
            self.size,
        )


class Section:
    def __init__(self, file, pos):
        self.blockHeader = BlockHeader(file, pos)
        self.data = file[pos + 8:pos + self.blockHeader.size]

    def save(self):
        self.blockHeader.size = 8 + len(self.data)
        return b''.join([self.blockHeader.save(), self.data])


class Head:
    user = "someone"
    host = "somewhere"
    date = "2019-01-19T22:30:54.551+09:00"
    source = ""
    title = None
    comment = None
    generatorName = "Layout Exporter U"
    generatorVersion = "1.0.0"

    def getAsDict(self):
        _dict = OrderedDict()
        _dict["create"] = OrderedDict()
        _dict["create"]["@user"] = self.user
        _dict["create"]["@host"] = self.host
        _dict["create"]["@date"] = self.date
        _dict["create"]["@source"] = self.source
        _dict["title"] = self.title
        _dict["comment"] = self.comment
        _dict["generator"] = OrderedDict()
        _dict["generator"]["@name"] = self.generatorName
        _dict["generator"]["@version"] = self.generatorVersion

        return _dict


class Color4:
    def __init__(self):
        self.r = 255
        self.g = 255
        self.b = 255
        self.a = 255

    def set(self, r, g, b, a):
        self.r, self.g, self.b, self.a = r, g, b, a

    def getAsDict(self):
        return {
            "@r": str(self.r),
            "@g": str(self.g),
            "@b": str(self.b),
            "@a": str(self.a),
        }


class MaterialName:
    def __init__(self):
        self.string = ""

    def set(self, string):
        assert len(string) <= 20
        self.string = string

    def get(self):
        return self.string


class UserData:
    class Item:
        def __init__(self):
            self.name = ""
            self.type = ""
            self.data = ""

        def set(self, userData):
            self.name = userData.name

            type = userData.type
            data = userData.data

            if type == 0:
                self.data = ' '.join(data)
                self.type = "string"

            elif type == 1:
                self.data = ' '.join([str(_int) for _int in data])
                self.type = "int"

            elif type == 2:
                self.data = ' '.join([str(_float) for _float in data])
                self.type = "float"

        def getAsDict(self):
            if self.type:
                return {
                    "@name": self.name,
                    "#text": self.data,
                }

            return None

    def __init__(self):
        self.string = []
        self.int = []
        self.float = []

    def set(self, extUserData):
        self.string = []
        self.int = []
        self.float = []

        for userData in extUserData:
            item = Item()
            item.set(userData)

            if item.type == "string":
                self.string.append(item.getAsDict())

            elif item.type == "int":
                self.int.append(item.getAsDict())

            elif item.type == "float":
                self.float.append(item.getAsDict())

    def setSingleStr(self, string):
        self.string = [{
            "@name": "__BasicUserDataString",
            "#text": string,
        }]

        self.int = []
        self.float = []

    def getAsDict(self):
        _dict = {}

        if self.string:
            _dict["string"] = self.string

        if self.int:
            _dict["int"] = self.int

        if self.float:
            _dict["float"] = self.float

        return _dict


class LRName:
    def __init__(self):
        self.string = ""

    def set(self, string):
        assert len(string) <= 24
        self.string = string

    def get(self):
        return self.string
