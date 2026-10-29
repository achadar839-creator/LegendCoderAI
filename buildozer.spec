[app]
title = Cosmic Coder
package.name = cosmiccoder
package.domain = com.cosmiccoder
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css,js,json,txt
version = 1.0
requirements_python = 3.10
requirements = python3,kivy,flask,requests,urllib3,jinja2

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO,WAKE_LOCK,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MICROPHONE
android.api = 33
android.ndk_api = 24
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
# p4a.branch = master
services = CosmicService:service.py
android.manifest.application_arguments = android:usesCleartextTraffic="true"
