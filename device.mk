#
# Copyright (C) 2023 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from the proprietary version
$(call inherit-product, vendor/xiaomi/fuxi-miuicamera/fuxi-miuicamera-vendor.mk)

# Shims for the prebuilt camera blobs
# c2.dolby.client.so links against dolbycodec_shim.so (it provides the old
# objcpy() overload that Android 17 renamed when BufferPoolSender became a
# template) and both camera JNI libraries link against
# libgui_shim_miuicamera.so (BnProducerListener::onBufferDetached). Neither
# is pulled in as a dependency of the prebuilt blob modules, so they have to
# be installed explicitly: without them the Dolby Codec2 store cannot be
# loaded and MIUI Camera finds no Dolby Vision encoder at all.
PRODUCT_PACKAGES += \
    dolbycodec_shim \
    libgui_shim_miuicamera

# Public libraries
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/public.libraries-xiaomi.txt:$(TARGET_COPY_OUT_SYSTEM)/etc/public.libraries-xiaomi.txt \
    $(LOCAL_PATH)/configs/public.libraries-miuicamera.txt:$(TARGET_COPY_OUT_VENDOR)/etc/public.libraries-miuicamera.txt

# Dolby Vision encoder declaration
# media_codecs_c2.xml is parsed by Codec2InfoBuilder in addition to the
# variant XML files, so the DV encoder is declared without replacing the
# vendor media_codecs_kalama.xml.
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/media/media_codecs_c2.xml:$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_c2.xml

# Priv-app permission
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/privapp-permissions-miuicamera.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/permissions/privapp-permissions-miuicamera.xml

# Soong namespaces
PRODUCT_SOONG_NAMESPACES += \
    $(LOCAL_PATH)

# Sysconfig
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/configs/miuicamera-hiddenapi-package-allowlist.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/sysconfig/miuicamera-hiddenapi-package-allowlist.xml
