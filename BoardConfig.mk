#
# Copyright (C) 2023 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from the proprietary version
include vendor/xiaomi/fuxi-miuicamera/BoardConfigVendor.mk

MIUICAMERA_PATH := device/xiaomi/fuxi-miuicamera

# Properties
TARGET_SYSTEM_PROP += $(MIUICAMERA_PATH)/system.prop
TARGET_VENDOR_PROP += $(MIUICAMERA_PATH)/vendor.prop
TARGET_ODM_PROP += $(MIUICAMERA_PATH)/configs/properties/odm_dolby.prop

# Dolby Vision (Dolby Codec2 component store)
DEVICE_MANIFEST_FILE += $(MIUICAMERA_PATH)/configs/vintf/c2_manifest_dolby.xml
DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE += $(MIUICAMERA_PATH)/configs/vintf/framework_matrix_dolby.xml

# Sepolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(MIUICAMERA_PATH)/sepolicy/vendor
