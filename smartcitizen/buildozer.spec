[app]

title = Smart Citizen

package.name = smartcitizen
package.domain = org.test

source.dir = .

source.include_exts = py,png,jpg,kv,atlas

source.exclude_dirs = old, bin, recherche, garden_graph_example

source.include_patterns = images/*.jpg,images/*.png

version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

requirements = python3,kivy,requests
garden_requirements = graph

orientation = all

fullscreen = 1

android.permissions = INTERNET

android.arch = armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1
