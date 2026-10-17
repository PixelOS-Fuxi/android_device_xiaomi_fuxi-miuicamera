/*
 * Copyright (C) 2026 The PixelOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Android 17 changed BufferPoolSender into a template
 * (android::BufferPoolSender<BufferPoolTypes>), which changed the mangled
 * name of the objcpy(WorkBundle*, const std::list<std::unique_ptr<C2Work>>&,
 * BufferPoolSender*) overload that the prebuilt Dolby Codec2 blobs reference
 * (frameworks/av/media/codec2/hal/hidl/1.0/utils/include/codec2/hidl/1.0/types.h).
 *
 * Without it c2.dolby.client.so has an unresolvable symbol and dolbycodec2
 * cannot dlopen it, so the Dolby Vision component store never registers.
 * Forward the old (untyped) symbol to the platform's typed overload instead of
 * stubbing it out, so the work bundle is still transferred properly.
 */

namespace android {
    extern "C" void _ZN7android8hardware5media2c24V1_05utils6objcpyEPNS3_10WorkBundleERKNSt3__14listINS7_10unique_ptrI6C2WorkNS7_14default_deleteISA_EEEENS7_9allocatorISD_EEEEPNS_16BufferPoolSenderINS4_15BufferPoolTypesEEE(
            void* thisptr, void* list, void* bufferPoolSender);

    extern "C" void _ZN7android8hardware5media2c24V1_05utils6objcpyEPNS3_10WorkBundleERKNSt3__14listINS7_10unique_ptrI6C2WorkNS7_14default_deleteISA_EEEENS7_9allocatorISD_EEEEPNS4_16BufferPoolSenderE(
            void* thisptr, void* list, void* bufferPoolSender) {
        _ZN7android8hardware5media2c24V1_05utils6objcpyEPNS3_10WorkBundleERKNSt3__14listINS7_10unique_ptrI6C2WorkNS7_14default_deleteISA_EEEENS7_9allocatorISD_EEEEPNS_16BufferPoolSenderINS4_15BufferPoolTypesEEE(
                thisptr, list, bufferPoolSender);
    }
}
