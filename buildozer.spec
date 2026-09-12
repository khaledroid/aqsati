[app]

title = Aqsati

package.name = aqsati

package.domain = org.aqsati

version = 1.1

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,ttf,json

android.permissions = INTERNET

android.api = 33

android.minapi = 21

android.ndk = 25b

android.archs = arm64-v8a

android.allow_backup = True

android.release_artifact = apk

orientation = portrait

fullscreen = 0

requirements = python3==3.11.11,hostpython3==3.11.11,kivy==2.3.0,kivymd==1.1.1,pillow,arabic_reshaper,python-bidi,openpyxl,fpdf2

p4a.source_dir = ./p4a

[buildozer]

log_level = 2

warn_on_root = 1
