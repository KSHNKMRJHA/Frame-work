[app]
title = FrameWork
package.name = framework
package.domain = org.framework
source.dir = .
source.include_exts = py,json,png,jpg,kv,atlas
version = 1.0.0

# Kivy is the only real dependency; quiz_logic.py has no external deps beyond
# the Python standard library (random, json).
requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1

[android]
# Minimum reasonable modern Android target; adjust as needed.
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
