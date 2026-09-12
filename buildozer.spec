[app]

# (str) Title of your application
title = Aqsati

# (str) Package name
package.name = aqsati

# (str) Package domain (needed for android/ios packaging)
package.domain = org.aqsati

# (str) Application versioning (method 1)
version = 1.0

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) NDK r28c: required for 16 KB page size support (Samsung S25 / Android 15)
# The earlier r28c failure was due to disk space, which is now fixed in the workflow.
android.ndk = 28c

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) The format used to package the app for release mode
android.release_artifact = apk

# (str) Orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Application requirements
# NOTE: NO pandas, NO reportlab, NO openpyxl here!
# Your code imports them inside try/except, so the APK works fine without them.
# NOTE: python3 and hostpython3 pinned to 3.11.11 (must match each other)
requirements = python3==3.11.11,hostpython3==3.11.11,kivy==2.3.0,kivymd==1.1.1,pillow,arabic_reshaper,python-bidi

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
