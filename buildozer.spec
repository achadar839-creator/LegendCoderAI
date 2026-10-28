[app]
title = Legend Coder AI
package.name = legendcoder
package.domain = org.ajay
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css,js
version = 1.0

requirements = python3,flask,werkzeug,jinja2,itsdangerous,click,blinker,markupsafe,six,urllib3

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.bootstrap = webview

[buildozer]
log_level = 2
warn_on_root = 1
