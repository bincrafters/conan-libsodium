#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class LibsodiumConan(ConanFile):
    name = "libsodium"
    version = "1.0.15"
    url = "https://github.com/bincrafters/conan-libsodium"
    description = "Sodium is a modern, easy-to-use software library for encryption, decryption, signatures, " \
                  "password hashing and more."
    license = "https://github.com/jedisct1/libsodium/blob/master/LICENSE"
    exports_sources = ["LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        source_url = "https://download.libsodium.org/libsodium/releases/libsodium-%s.tar.gz" % self.version
        tools.get(source_url)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build_vs(self):
        cmd = tools.msvc_build_command(self.settings, "libsodium.sln", upgrade_project=False)
        with tools.chdir('sources'):
            if self.settings.arch == "x86":
                cmd = cmd.replace("x86", "Win32")
            # skip unit tests
            cmd += " /p:PostBuildEventUseInBuild=false"
            self.run(cmd)

    def build_configure(self):
        with tools.chdir('sources'):
            args = ['--prefix=%s' % self.package_folder]
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_vs()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src='sources')
        if self.settings.compiler == 'Visual Studio':
            self.copy("*.h", dst="include", src=os.path.join("sources", "src", "libsodium", "include"))
            self.copy("*.lib", dst="lib", src="sources", keep_path=False)
            self.copy("*.dll", dst="bin", src="sources", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == 'Visual Studio':
            if not self.options.shared:
                self.cpp_info.defines.append('SODIUM_STATIC')
