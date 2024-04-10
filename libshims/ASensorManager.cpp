/*
 * Copyright (C) 2020 LineageOS Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <ALooper.h>

#define LOG_TAG "libshim_sensorndkbridge"
#include <android-base/logging.h>

using android::Mutex;

static Mutex gLock;

extern "C" ALooper *ALooper_forCamera() {
    LOG(VERBOSE) << "ALooper_forCamera";
    ALooper *sLooper = NULL;

    Mutex::Autolock autoLock(gLock);
    sLooper = new ALooper;

    return sLooper;
}

extern "C" int ALooper_release_forCamera(ALooper *sLooper) {
    if (sLooper != nullptr) {
        Mutex::Autolock autoLock(gLock);
        delete sLooper;
    }

    return 0;
}

extern "C" int ALooper_pollOnce_camera(ALooper *sLooper,
                                       int timeoutMillis,
                                       int* outFd,
                                       int* outEvents,
                                       void** outData) {
    int res = sLooper->pollOnce(timeoutMillis, outFd, outEvents, outData);
    LOG(VERBOSE) << "ALooper_pollOnce_camera => " << res;
    return res;
}
