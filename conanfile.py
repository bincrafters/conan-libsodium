#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
import os


class LibsodiumConan(ConanFile):
    name = "libsodium"
    version = "1.0.18"
    url = "https://github.com/bincrafters/conan-libsodium"
    homepage = "https://github.com/jedisct1/libsodium"
    description = "Sodium is a modern, easy-to-use software library for encryption, decryption, signatures, " \
                  "password hashing and more."
    license = "ISC"
    author = "Bincrafters <bincrafters@gmail.com>"
    topics = ("conan", "sodium", "libsodium", "encryption", "signature", "hashing")
    exports_sources = ["LICENSE.md", "FindSodium.cmake"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    short_paths = True
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.stdcpp
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        sha256 = "6f504490b342a4f8a4c4a02fc9b866cbef8622d5df4e5452b46be121e46636c1"
        source_url = "https://download.libsodium.org/libsodium/releases/libsodium-%s.tar.gz" % self.version
        tools.get(source_url, sha256=sha256)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_vs(self):
        runtime_library = {'MT': 'MultiThreaded',
                           'MTd': 'MultiThreadedDebug',
                           'MD': 'MultiThreadedDLL',
                           'MDd': 'MultiThreadedDebugDLL'}.get(str(self.settings.compiler.runtime))
        if self.options.shared:
            build_type = 'DynDebug' if self.settings.build_type == 'Debug' else 'DynRelease'
        else:
            build_type = 'StaticDebug' if self.settings.build_type == 'Debug' else 'StaticRelease'
        msbuild = MSBuild(self)
        msvc = {'10': 'vs2010',
                '11': 'vs2012',
                '12': 'vs2013',
                '14': 'vs2015',
                '15': 'vs2017',
                '16': 'vs2017',
                '16': 'vs2019',}.get(str(self.settings.compiler.version))
        with tools.chdir(os.path.join(self._source_subfolder, 'builds', 'msvc', msvc)):
            runtime = '<ClCompile><RuntimeLibrary>%s</RuntimeLibrary>' % runtime_library
            tools.replace_in_file(os.path.join('libsodium', 'libsodium.props'), '<ClCompile>', runtime)

            msbuild.build("libsodium.sln", build_type=build_type,
                          upgrade_project=False, platforms={"x86": "Win32"},
                          properties={"PostBuildEventUseInBuild": "false"})

    def _configure_autotools(self):
        if not self._autotools:
            args = ['--prefix=%s' % self.package_folder]
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            if self.options.fPIC:
                args.append('--with-pic')
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self._build_vs()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="FindSodium.cmake")
        if self.settings.compiler == 'Visual Studio':
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "src", "libsodium", "include"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            self.copy("*.dll", dst="bin", src=self._source_subfolder, keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('SODIUM_STATIC')
