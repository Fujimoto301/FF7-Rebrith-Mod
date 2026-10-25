"""
loosezen.py — load loose FF7 Rebirth Zen .uasset exports with pyUE4Parse,
without game containers: script-object hashes are resolved via CityHash64
brute force over the package name map (no global.utoc needed).
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vendorpath                 # bundled UE4Parse when none is installed
vendorpath.require()
from cityhash import script_object_hash

from UE4Parse.BinaryReader import BinaryStream
from UE4Parse.Assets.PackageReader import IoPackageReader, EPackageLoadMode
from UE4Parse.Versions import VersionContainer, EUEVersion
from UE4Parse.Provider.MappingProvider import MappingProvider
from UE4Parse.Assets.Objects.FName import FName
from UE4Parse.IoObjects.FPackageObjectIndex import FPackageObjectIndex

# CompiledData templates are huge (up to ~1MB) and we parse them separately with
# a byte scanner — skip deserialization entirely for speed.
from UE4Parse.Assets.Exports import ExportRegistry
from UE4Parse.Assets.Exports.UObjects import UObject as _UObject

class _SkipExport(_UObject):
    def deserialize(self, validpos):
        pass

ExportRegistry.exports['MovieSceneCompiledData'] = _SkipExport


def _null_poi():
    inst = object.__new__(FPackageObjectIndex)
    inst._typeAndId = FPackageObjectIndex.Invalid
    return inst


class FakeScriptDesc:
    def __init__(self, name):
        self.Name = FName(name)
        self.FullName = FName(name)
        self.OuterIndex = _null_poi()


class FakeGlobalData:
    def __init__(self):
        self.ScriptObjectByGlobalId = {}


class FakeProvider:
    def __init__(self, mappings, ue=EUEVersion.GAME_UE4_26):
        self.Versions = VersionContainer(ue)
        self.GlobalData = FakeGlobalData()
        self.Triggers = {}
        self.mappings = mappings

    def try_load_package(self, *a, **k):
        return None


def read_names(path):
    d = open(path, 'rb').read()
    nmO, nmS = struct.unpack_from('<ii', d, 24)
    names = []
    o = nmO
    while o < nmO + nmS:
        b0, b1 = d[o], d[o+1]; o += 2
        utf16 = b0 >> 7; ln = ((b0 & 0x7f) << 8) | b1
        if utf16:
            names.append(d[o:o+2*ln].decode('utf-16-le')); o += 2*ln
        else:
            names.append(d[o:o+ln].decode('latin1')); o += ln
    return names


SCRIPT_TYPE = 1 << 62


def build_script_table(names, extra_names=()):
    """Map FPackageObjectIndex typeAndId -> FakeScriptDesc for all plausible
    /Script/Module.Object combos from the name map."""
    mods = [n for n in names if n.startswith('/Script/')]
    simple = [n for n in names if not n.startswith('/')] + list(extra_names)
    table = {}
    for m in mods:
        h = script_object_hash(m) | SCRIPT_TYPE
        table[h] = FakeScriptDesc(m)
        for n in simple:
            for form in ('%s.%s' % (m, n), '%s.Default__%s' % (m, n)):
                table[script_object_hash(form) | SCRIPT_TYPE] = FakeScriptDesc(n if '.' not in form or 'Default__' not in form else 'Default__' + n)
    return table


_MAPPINGS = None

def get_mappings(usmap_path):
    global _MAPPINGS
    if _MAPPINGS is None:
        _MAPPINGS = MappingProvider(usmap_path)
    return _MAPPINGS


def load_package(uasset_path, usmap_path, ue=EUEVersion.GAME_UE4_26):
    mappings = get_mappings(usmap_path)
    provider = FakeProvider(mappings, ue)
    names = read_names(uasset_path)
    provider.GlobalData.ScriptObjectByGlobalId = build_script_table(names)
    stream = BinaryStream(uasset_path)
    stream.mappings = mappings
    pkg = IoPackageReader(stream, None, None, provider, EPackageLoadMode.Full)
    return pkg


if __name__ == '__main__':
    import json
    pkg = load_package(sys.argv[1], sys.argv[2])
    print(json.dumps(pkg.get_dict(), indent=1, default=str)[:8000])
