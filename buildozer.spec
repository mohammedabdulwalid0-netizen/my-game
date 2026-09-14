[app]
title = My Game
package.name = mygame
package.domain = com.mygame.app
source.dir =.
source.include_exts = py,png,jpg,atlas,wav,mp3,ttf
version = 0.1
requirements = python3,pygame
orientation = landscape
fullscreen = 0

[buildozer]
log_level = 2

[app:android]
p4a.bootstrap = sdl2

[buildozer:android]
android.accept_sdk_license_agreement = True
