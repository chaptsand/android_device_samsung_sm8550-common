/*
 * Copyright (C) 2025 The LineageOS Project
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

/*
 * Board specific nodes
 *
 * If your kernel exposes these controls in another place, you can either
 * symlink to the locations given here, or override this header in your
 * device tree.
 */
#define PANEL_BRIGHTNESS_NODE "/sys/class/backlight/panel0-backlight/brightness"
#define PANEL_MAX_BRIGHTNESS_NODE "/sys/class/backlight/panel0-backlight/max_brightness"
