[app]
title = Kocina del Mundo
package.name = kocinadelmundo
package.domain = org.imadlocco

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy

orientation = portrait
fullscreen = 0

# icon.filename = %(source.dir)s/icon.png   <- descomenta esta línea cuando subas tu logo como icon.png

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1