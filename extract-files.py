#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/samsung/sm8550-common',
    'hardware/qcom-caf/sm8550',
    'hardware/qcom-caf/wlan',
    'hardware/samsung',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'vendor.qti.diaghal@1.0',
        'libsecril-client',
        'vendor.qti.hardware.fm@1.0',
    ): lib_fixup_vendor_suffix,
    (
        'libagmclient',
        'libpalclient',
    ): lib_fixup_remove,
}

blob_fixups: blob_fixups_user_type = {
    ('vendor/bin/hw/android.hardware.security.keymint-service-qti', 'vendor/lib64/libskeymint10device.so', 'vendor/lib64/libskeymint_cli.so'): blob_fixup()
        .add_needed('android.hardware.security.rkp-V3-ndk.so')
        .replace_needed('libcrypto.so', 'libcrypto-v33.so')
        .replace_needed('libcppbor_external.so', 'libcppbor.so'),
    'vendor/lib64/hw/gatekeeper.mdfpp.so': blob_fixup()
        .replace_needed('libcrypto.so', 'libcrypto-v33.so'),
    'vendor/lib64/libsec-ril.so': blob_fixup()
        .binary_regex_replace(b'ril.dds.call.ongoing', b'vendor.calls.slot_id')
        .sig_replace('60 0E 40 F9 E1 03 15 AA 82 0C 80 52 E3 03 14 AA', '60 0E 40 F9 E1 03 15 AA 82 0C 80 52 30 08 0D D2'),
    'vendor/etc/vintf/manifest/sec_c2_manifest_default0_1_0.xml': blob_fixup()
        .regex_replace('default0', 'software'),
    'vendor/etc/init/vendor.qti.media.c2audio@1.0-service.rc': blob_fixup()
        .regex_replace('.*disabled.*\n', ''),
    ('vendor/etc/media_codecs_kalama.xml', 'vendor/etc/media_codecs_kalama_vendor.xml'): blob_fixup()
        .regex_replace('.*media_codecs_(google_audio|google_c2|google_telephony|google_video|vendor_audio).*\n', ''),
    'vendor/etc/seccomp_policy/atfwd@2.0.policy': blob_fixup()
        .add_line_if_missing('gettid: 1'),
    'vendor/etc/seccomp_policy/qwesd@2.0.policy': blob_fixup()
        .add_line_if_missing('gettid: 1')
        .add_line_if_missing('pipe2: 1'),
    'vendor/lib64/libqcodec2_core.so': blob_fixup()
        .add_needed('libcodec2_shim.so'),
    'vendor/lib64/unihal_android.so': blob_fixup()
        .add_needed('libui_shim.so'),
    'vendor/lib64/libsamsungcamerahal.so': blob_fixup()
        .sig_replace('E0 8A', '94 8B'),
    'vendor/etc/init/android.hardware.security.keymint-service-qti.rc': blob_fixup()
        .regex_replace('android.hardware.security.keymint-service', 'android.hardware.security.keymint-service-qti'),
}  # fmt: skip

module = ExtractUtilsModule(
    'sm8550-common',
    'samsung',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
