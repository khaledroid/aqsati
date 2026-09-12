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

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

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
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow,arabic_reshaper,python-bidi

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
