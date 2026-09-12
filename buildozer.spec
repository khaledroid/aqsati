[app]

# (str) Title of your application
title = Aqsati

# (str) Package name
package.name = aqsati

# (str) Package domain (needed for android/ios packaging)
package.domain = org.aqsati

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (str) Icon of the application
#icon.filename = icon.png

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (list) The Android archs to build for
android.archs = arm64-v8a

# (str) The Android NDK version to use
#android.ndk = 25b

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

# (str) Orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Application requirements
# NOTE: NO pandas, NO reportlab, NO openpyxl here!
# Your code imports them inside try/except, so the APK works fine without them.
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow,arabic_reshaper,python-bidi

# (str) Presplash of the application
#presplash.filename = presplash.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
#orientation = portrait

# (str) The format used to package the app for release mode (aab or apk or aar).
#android.release_artifact = aab

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
