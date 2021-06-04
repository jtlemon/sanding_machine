pyside2-rcc assets/app_resources.qrc -o app_resources_rc.py

pyside2-uic forms/dovetail_camera_page.ui -o views/generated/dovetail_camera_page.py
pyside2-uic forms/reset_page.ui -o views/generated/reset_page.py