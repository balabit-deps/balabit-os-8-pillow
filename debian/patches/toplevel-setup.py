--- a/setup.py
+++ b/setup.py
@@ -8,6 +8,9 @@
 # Your cheese is so fresh most people think it's a cream: Mascarpone
 # ------------------------------
 
+from sysconfig import get_platform
+host_platform = get_platform()
+
 import os
 import re
 import struct
@@ -38,7 +41,7 @@ TIFF_ROOT = None
 ZLIB_ROOT = None
 
 
-if sys.platform == "win32" and sys.version_info >= (3, 9):
+if host_platform == "win32" and sys.version_info >= (3, 9):
     warnings.warn(
         "Pillow {} does not support Python {}.{} and does not provide prebuilt "
         "Windows binaries. We do not recommend building from source on Windows.".format(
@@ -134,7 +137,7 @@ class RequiredDependencyException(Except
 PLATFORM_MINGW = "mingw" in ccompiler.get_default_compiler()
 PLATFORM_PYPY = hasattr(sys, "pypy_version_info")
 
-if sys.platform == "win32" and PLATFORM_MINGW:
+if host_platform == "win32" and PLATFORM_MINGW:
     from distutils import cygwinccompiler
 
     cygwin_versions = cygwinccompiler.get_versions()
@@ -158,7 +161,7 @@ def _dbg(s, tp=None):
 def _find_library_dirs_ldconfig():
     # Based on ctypes.util from Python 2
 
-    if sys.platform.startswith("linux") or sys.platform.startswith("gnu"):
+    if host_platform.startswith("linux") or host_platform.startswith("gnu"):
         if struct.calcsize("l") == 4:
             machine = os.uname()[4] + "-32"
         else:
@@ -180,7 +183,7 @@ def _find_library_dirs_ldconfig():
         env["LC_ALL"] = "C"
         env["LANG"] = "C"
 
-    elif sys.platform.startswith("freebsd"):
+    elif host_platform.startswith("freebsd"):
         args = ["/sbin/ldconfig", "-r"]
         expr = r".* => (.*)"
         env = {}
@@ -351,6 +354,38 @@ class pil_build_ext(build_ext):
                 _dbg("Requiring %s", x)
                 self.feature.required.add(x)
 
+    def add_gcc_paths(self):
+        gcc = sysconfig.get_config_var('CC')
+        tmpfile = os.path.join(self.build_temp, 'gccpaths')
+        if not os.path.exists(self.build_temp):
+            os.makedirs(self.build_temp)
+        ret = os.system('%s -E -v - </dev/null 2>%s 1>/dev/null' % (gcc, tmpfile))
+        is_gcc = False
+        in_incdirs = False
+        inc_dirs = []
+        lib_dirs = []
+        try:
+            if ret >> 8 == 0:
+                with open(tmpfile) as fp:
+                    for line in fp.readlines():
+                        if line.startswith("gcc version"):
+                            is_gcc = True
+                        elif line.startswith("#include <...>"):
+                            in_incdirs = True
+                        elif line.startswith("End of search list"):
+                            in_incdirs = False
+                        elif is_gcc and line.startswith("LIBRARY_PATH"):
+                            for d in line.strip().split("=")[1].split(":"):
+                                d = os.path.normpath(d)
+                                if '/gcc/' not in d:
+                                    _add_directory(self.compiler.library_dirs,
+                                                   d)
+                        elif is_gcc and in_incdirs and '/gcc/' not in line:
+                            _add_directory(self.compiler.include_dirs,
+                                           line.strip())
+        finally:
+            os.unlink(tmpfile)
+
     def build_extensions(self):
 
         library_dirs = []
@@ -428,7 +463,7 @@ class pil_build_ext(build_ext):
         if self.disable_platform_guessing:
             pass
 
-        elif sys.platform == "cygwin":
+        elif host_platform == "cygwin":
             # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
             _add_directory(
                 library_dirs,
@@ -437,7 +472,7 @@ class pil_build_ext(build_ext):
                 ),
             )
 
-        elif sys.platform == "darwin":
+        elif host_platform == "darwin":
             # attempt to make sure we pick freetype2 over other versions
             _add_directory(include_dirs, "/sw/include/freetype2")
             _add_directory(include_dirs, "/sw/lib/freetype2/include")
@@ -478,13 +513,13 @@ class pil_build_ext(build_ext):
                 _add_directory(include_dirs, "/usr/X11/include")
 
         elif (
-            sys.platform.startswith("linux")
-            or sys.platform.startswith("gnu")
-            or sys.platform.startswith("freebsd")
+            host_platform.startswith("linux")
+            or host_platform.startswith("gnu")
+            or host_platform.startswith("freebsd")
         ):
             for dirname in _find_library_dirs_ldconfig():
                 _add_directory(library_dirs, dirname)
-            if sys.platform.startswith("linux") and os.environ.get(
+            if host_platform.startswith("linux") and os.environ.get(
                 "ANDROID_ROOT", None
             ):
                 # termux support for android.
@@ -495,11 +530,11 @@ class pil_build_ext(build_ext):
                     library_dirs, os.path.join(os.environ["ANDROID_ROOT"], "lib")
                 )
 
-        elif sys.platform.startswith("netbsd"):
+        elif host_platform.startswith("netbsd"):
             _add_directory(library_dirs, "/usr/pkg/lib")
             _add_directory(include_dirs, "/usr/pkg/include")
 
-        elif sys.platform.startswith("sunos5"):
+        elif host_platform.startswith("sunos5"):
             _add_directory(library_dirs, "/opt/local/lib")
             _add_directory(include_dirs, "/opt/local/include")
 
@@ -515,7 +550,7 @@ class pil_build_ext(build_ext):
             # alpine, at least
             _add_directory(library_dirs, "/lib")
 
-        if sys.platform == "win32":
+        if host_platform == "win32":
             if PLATFORM_MINGW:
                 _add_directory(
                     include_dirs, "C:\\msys64\\mingw32\\include\\libimagequant"
@@ -555,7 +590,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "zlib.h"):
                 if _find_library_file(self, "z"):
                     feature.zlib = "z"
-                elif sys.platform == "win32" and _find_library_file(self, "zlib"):
+                elif host_platform == "win32" and _find_library_file(self, "zlib"):
                     feature.zlib = "zlib"  # alternative name
 
         if feature.want("jpeg"):
@@ -563,7 +598,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "jpeglib.h"):
                 if _find_library_file(self, "jpeg"):
                     feature.jpeg = "jpeg"
-                elif sys.platform == "win32" and _find_library_file(self, "libjpeg"):
+                elif host_platform == "win32" and _find_library_file(self, "libjpeg"):
                     feature.jpeg = "libjpeg"  # alternative name
 
         feature.openjpeg_version = None
@@ -619,7 +654,7 @@ class pil_build_ext(build_ext):
             if _find_include_file(self, "tiff.h"):
                 if _find_library_file(self, "tiff"):
                     feature.tiff = "tiff"
-                if sys.platform in ["win32", "darwin"] and _find_library_file(
+                if host_platform in ["win32", "darwin"] and _find_library_file(
                     self, "libtiff"
                 ):
                     feature.tiff = "libtiff"
@@ -704,7 +739,7 @@ class pil_build_ext(build_ext):
         if feature.jpeg2000:
             libs.append(feature.jpeg2000)
             defs.append(("HAVE_OPENJPEG", None))
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 defs.append(("OPJ_STATIC", None))
         if feature.zlib:
             libs.append(feature.zlib)
@@ -715,12 +750,12 @@ class pil_build_ext(build_ext):
         if feature.tiff:
             libs.append(feature.tiff)
             defs.append(("HAVE_LIBTIFF", None))
-        if sys.platform == "win32":
+        if host_platform == "win32":
             libs.extend(["kernel32", "user32", "gdi32"])
         if struct.unpack("h", b"\0\1")[0] == 1:
             defs.append(("WORDS_BIGENDIAN", None))
 
-        if sys.platform == "win32" and not (PLATFORM_PYPY or PLATFORM_MINGW):
+        if host_platform == "win32" and not (PLATFORM_PYPY or PLATFORM_MINGW):
             defs.append(("PILLOW_VERSION", '"\\"%s\\""' % PILLOW_VERSION))
         else:
             defs.append(("PILLOW_VERSION", '"%s"' % PILLOW_VERSION))
@@ -744,7 +779,7 @@ class pil_build_ext(build_ext):
 
         if feature.lcms:
             extra = []
-            if sys.platform == "win32":
+            if host_platform == "win32":
                 extra.extend(["user32", "gdi32"])
             exts.append(
                 Extension(
@@ -769,7 +804,7 @@ class pil_build_ext(build_ext):
                 )
             )
 
-        tk_libs = ["psapi"] if sys.platform == "win32" else []
+        tk_libs = ["psapi"] if host_platform == "win32" else []
         exts.append(
             Extension(
                 "PIL._imagingtk",
@@ -798,7 +833,7 @@ class pil_build_ext(build_ext):
         print("-" * 68)
         print("version      Pillow %s" % PILLOW_VERSION)
         v = sys.version.split("[")
-        print("platform     {} {}".format(sys.platform, v[0].strip()))
+        print("platform     {} {}".format(host_platform, v[0].strip()))
         for v in v[1:]:
             print("             [%s" % v.strip())
         print("-" * 68)
