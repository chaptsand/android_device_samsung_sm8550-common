#!/bin/bash
#
# Copyright (C) 2016 The CyanogenMod Project
# Copyright (C) 2017-2020 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

set -e

# Load extract_utils and do some sanity checks
MY_DIR="${BASH_SOURCE%/*}"
if [[ ! -d "${MY_DIR}" ]]; then MY_DIR="${PWD}"; fi

ANDROID_ROOT="${MY_DIR}/../../.."

HELPER="${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
if [ ! -f "${HELPER}" ]; then
    echo "Unable to find helper script at ${HELPER}"
    exit 1
fi
source "${HELPER}"

# Default to sanitizing the vendor folder before extraction
CLEAN_VENDOR=true

ONLY_COMMON=
ONLY_TARGET=
KANG=
SECTION=

while [ "${#}" -gt 0 ]; do
    case "${1}" in
        --only-common )
                ONLY_COMMON=true
                ;;
        --only-target )
                ONLY_TARGET=true
                ;;
        -n | --no-cleanup )
                CLEAN_VENDOR=false
                ;;
        -k | --kang )
                KANG="--kang"
                ;;
        -s | --section )
                SECTION="${2}"; shift
                CLEAN_VENDOR=false
                ;;
        * )
                SRC="${1}"
                ;;
    esac
    shift
done

if [ -z "${SRC}" ]; then
    SRC="adb"
fi

function blob_fixup() {
    case "${1}" in
        vendor/bin/hw/android.hardware.security.keymint-service)
            grep -q "android.hardware.security.rkp-V3-ndk.so" "${2}" || ${PATCHELF} --add-needed "android.hardware.security.rkp-V3-ndk.so" "${2}"
            ${PATCHELF} --replace-needed libcrypto.so libcrypto-v33.so "${2}"
            ;;
        vendor/lib64/hw/gatekeeper.mdfpp.so)
            ${PATCHELF} --replace-needed libcrypto.so libcrypto-v33.so "${2}"
            ;;
        vendor/lib64/libsec-ril.so)
            xxd -p -c0 "${2}" | sed "s/600e40f9e10315aa820c8052e30314aa/600e40f9e10315aa820c8052030080d2/g" | xxd -r -p > "${2}".patched
            mv "${2}".patched "${2}"
            sed -i 's/ril.dds.call.ongoing/vendor.calls.slot_id/g' "${2}"
            ;;
        vendor/etc/vintf/manifest/sec_c2_manifest_default0_1_0.xml)
            sed -i 's/default0/software/g' "${2}"
            ;;
        vendor/etc/media_codecs_kalama.xml|vendor/etc/media_codecs_kalama_vendor.xml)
            sed -Ei "/media_codecs_(google_audio|google_telephony|google_video|vendor_audio)/d" "${2}"
            ;;
        vendor/etc/seccomp_policy/qwesd@2.0.policy)
            echo "pipe2: 1" >> "${2}"
	    ;;
	vendor/etc/init/vendor.qti.media.c2audio@1.0-service.rc)
            sed -i '/disabled/d' "${2}"
            ;;
    esac
}

if [ -z "${ONLY_TARGET}" ]; then
    # Initialize the helper for common device
    setup_vendor "${DEVICE_COMMON}" "${VENDOR_COMMON:-$VENDOR}" "${ANDROID_ROOT}" true "${CLEAN_VENDOR}"

    extract "${MY_DIR}/proprietary-files.txt" "${SRC}" "${KANG}" --section "${SECTION}"
fi

if [ -z "${ONLY_COMMON}" ] && [ -s "${MY_DIR}/../../${VENDOR}/${DEVICE}/proprietary-files.txt" ]; then
    # Reinitialize the helper for device
    source "${MY_DIR}/../../${VENDOR}/${DEVICE}/extract-files.sh"
    setup_vendor "${DEVICE}" "${VENDOR}" "${ANDROID_ROOT}" false "${CLEAN_VENDOR}"

    extract "${MY_DIR}/../../${VENDOR}/${DEVICE}/proprietary-files.txt" "${SRC}" "${KANG}" --section "${SECTION}"
fi

"${MY_DIR}/setup-makefiles.sh"
