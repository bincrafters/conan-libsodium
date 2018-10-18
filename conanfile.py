#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild


class LibsodiumConan(ConanFile):
    name = "libsodium"
    version = "1.0.16"
    url = "https://github.com/bincrafters/conan-libsodium"
    homepage = "https://github.com/jedisct1/libsodium"
    description = "Sodium is a modern, easy-to-use software library for encryption, decryption, signatures, " \
                  "password hashing and more."
    license = "https://github.com/jedisct1/libsodium/blob/master/LICENSE"
    exports_sources = ["LICENSE.md", "FindSodium.cmake"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    short_paths = True
    _source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def source(self):
        source_url = "https://download.libsodium.org/libsodium/releases/libsodium-%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_vs(self):
        msbuild = MSBuild(self)
        if self.options.shared:
            build_type = "DynDebug" if self.settings.build_type == "Debug" else "DynRelease"
        else:
            build_type = "StaticDebug" if self.settings.build_type == "Debug" else "StaticRelease"
        msvc = {"10": "vs2010",
                "11": "vs2012",
                "12": "vs2013",
                "14": "vs2015",
                "15": "vs2017"}.get(str(self.settings.compiler.version))
        with tools.chdir(os.path.join(self._source_subfolder, "builds", "msvc", msvc)):
            msbuild.build("libsodium.sln", build_type=build_type,
                          upgrade_project=False, platforms={"x86": "Win32"},
                          properties={"PostBuildEventUseInBuild": "false"})

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            args = []
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            if self.settings.build_type == "Debug":
                args.append("--enable-debug")
            if self.options.fPIC:
                args.append("--with-pic")
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_vs()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder)
        self.copy(pattern="FindSodium.cmake")
        if self.settings.compiler == "Visual Studio":
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src", "libsodium", "include"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            self.copy("*.dll", dst="bin", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("SODIUM_STATIC")
