# [SublimeLinter @python:3]

import ctypes
import comtypes.client as cc

if not ctypes.windll.shell32.IsUserAnAdmin():
    raise ValueError("Should be run with admin rights!")

cc.GetModule("build/ShObjIdl_core.tlb")
cc.GetModule("build/ShObjIdl.tlb")

print("gen_comtypes_cache.py: done!")
