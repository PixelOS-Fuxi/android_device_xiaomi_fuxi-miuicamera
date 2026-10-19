#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import os
import stat
from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

from extract_utils.utils import (
    Color,
    color_print,
)

namespace_imports = [
    'device/xiaomi/fuxi-miuicamera',
]


def lib_fixup_system_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'system' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    'vendor.xiaomi.hardware.campostproc@1.0': lib_fixup_system_suffix,
}

# The Dolby HEVC blobs allocate a GraphicBuffer-sized object with operator new
# right after UnwrapNativeCodec2GrallocHandle and reserve 0x100 bytes for it:
#
#     mov  x20, x0            <- unwrapped handle
#     mov  w0, #0x100         <- size passed to operator new
#     bl   _Znwm
#
# libui writes that object through offset 0xd28, so 256 bytes overrun the heap
# while Dolby Vision metadata is generated. Reserve 0x1000 instead.
#
# The mov is paired with the following operator new call to keep the pattern
# unique: c2.dolby.hevc.enc.so also carries an unrelated "mov w0, #0x100" at
# 0x1d4c8 (C2AndroidMemoryUsage::FromGrallocUsage), so do not shorten it.
GRAPHICBUFFER_ALLOC_ENCODER = (b'\x00\x20\x80\x52\x03\x42\x00\x94',
                               b'\x00\x00\x82\x52\x03\x42\x00\x94')
GRAPHICBUFFER_ALLOC_DECODER = (b'\x00\x20\x80\x52\x74\x54\x00\x94',
                               b'\x00\x00\x82\x52\x74\x54\x00\x94')

# dolbycodec2 allocates the Codec2 HIDL component store wrapper with operator
# new, using the sizeof() value it was compiled against on Android 16:
#
#     mov  w0, #0x108         <- size passed to operator new
#     bl   _Znwm
#     bl   ...utils::ComponentStore::ComponentStore(shared_ptr<C2ComponentStore>)
#
# android::hardware::media::c2::V1_0::utils::ComponentStore grew to 0x120 in
# Android 17 (RefBase moved from +0xf8 to +0x110, mRefs from +0x100 to +0x118).
# scudo rounds new(0x108) to a 0x120 byte chunk with a 16 byte header, leaving
# 0x110 usable bytes, so the constructor's write of mRefs lands 16 bytes past
# the allocation - on the next chunk's header. The HIDL thread later calls
# decStrong() on that store and dereferences the mRefs that was written
# out of bounds, which was observed as a SIGSEGV at RefBase::decStrong+28 with
# x19 (mRefs) == 0, called from
# BnHwComponentStore::_hidl_createInterface (tombstone_17.pb).
#
# Reserve 0x120 instead: new(0x120) lands in the 0x160 byte chunk class, giving
# 0x150 usable bytes. 0x120 is also the exact sizeof(ComponentStore) of the
# Android 17 build, as proven by the `mov w1, #0x120` in the deleting destructor
# of libcodec2_hidl@1.0.so.
#
# The mov is paired with the following operator new call to keep the pattern
# unique: 0x108 also appears as the CAM_FLUSH_REQ opcode in the camera kernel,
# which is unrelated.
DOLBY_CODEC2_STORE_SIZE = (b'\x00\x21\x80\x52',
                           b'\x00\x24\x80\x52')

def blob_fixup_split_file(
    ctx: 'BlobFixupCtx',
    file: 'File',
    file_path: str,
    *args,
    **kwargs,
):
    # Split the file into parts
    part_size = 51380224 # 49 MiB
    part_number = 0
    with open(file_path, 'rb') as f:
        while chunk := f.read(part_size):
            part_file_name = f"{file_path}.part{part_number:02d}"
            with open(part_file_name, 'wb') as part_file:
                part_file.write(chunk)
            part_number += 1
    color_print(f'{file.dst}: split into {part_number} parts', color=Color.GREEN)

    # Add the file to .gitignore
    gitignore_path = os.path.join(module.vendor_path, '.gitignore')
    with open(gitignore_path, 'a+') as gitignore_file:
        gitignore_file.seek(0)  # Move to the start of the file
        existing_entries = gitignore_file.read().splitlines()
        if f'proprietary/{file.dst}' not in existing_entries:
            gitignore_file.write(f'proprietary/{file.dst}\n')
            color_print(f'{file.dst}: added to .gitignore', color=Color.GREEN)

blob_fixups: blob_fixups_user_type = {
    'system/lib64/libcamera_algoup_jni.xiaomi.so': blob_fixup()
        .add_needed('libgui_shim_miuicamera.so')
        .sig_replace('08 AD 40 F9', '08 A9 40 F9'),
    'system/lib64/libcamera_mianode_jni.xiaomi.so': blob_fixup()
        .add_needed('libgui_shim_miuicamera.so'),
    'system/lib64/libmicampostproc_client.so': blob_fixup()
        .remove_needed('libhidltransport.so'),
    'system/priv-app/MiuiCamera/MiuiCamera.apk': blob_fixup()
        .apktool_patch('patches')
        .call(blob_fixup_split_file),
    'vendor/bin/hw/dolbycodec2': blob_fixup()
        .binary_regex_replace(*DOLBY_CODEC2_STORE_SIZE),
    'vendor/lib64/c2.dolby.client.so': blob_fixup()
        .add_needed('dolbycodec_shim.so'),
    'vendor/lib64/c2.dolby.hevc.enc.so': blob_fixup()
        .binary_regex_replace(*GRAPHICBUFFER_ALLOC_ENCODER),
    'vendor/lib64/c2.dolby.hevc.dec.so': blob_fixup()
        .binary_regex_replace(*GRAPHICBUFFER_ALLOC_DECODER),
    'vendor/lib64/c2.dolby.hevc.sec.dec.so': blob_fixup()
        .binary_regex_replace(*GRAPHICBUFFER_ALLOC_DECODER),
}  # fmt: skip

module = ExtractUtilsModule(
    'fuxi-miuicamera',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

def generate_vendorsetup_script():
    vendorsetup_path = os.path.join(module.vendor_path, "vendorsetup.sh")
    with open(vendorsetup_path, 'w') as setup_file:
        setup_file.write('#!/bin/bash\n')
        setup_file.write('# Script to dynamically reassemble .part* files\n\n')
        setup_file.write(f'for file in $(find \"{module.vendor_rel_path}\" -type f -name \"*.part00\"); do\n')
        setup_file.write('    base_name=${file%.part00}\n')
        setup_file.write('    cat ${base_name}.part* > $base_name\n')
        setup_file.write('    echo \"Reassembly of $base_name complete!\"\n')
        setup_file.write('done\n')
    os.chmod(vendorsetup_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    color_print(f'Generated dynamic reassembly script: vendorsetup.sh', color=Color.END)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
    generate_vendorsetup_script()
