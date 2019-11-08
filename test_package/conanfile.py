from conans import ConanFile, CMake, tools, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        for variant in ['CONAN', 'CONAN_TARGETS', 'FIND_PACKAGE', 'FIND_PACKAGE_TARGETS']:
            cmake = CMake(self)
            cmake.definitions['BUILD_VARIANT'] = variant
            cmake.configure(build_dir=variant)
            cmake.build()

    def test(self):
        for variant in ['CONAN', 'CONAN_TARGETS', 'FIND_PACKAGE', 'FIND_PACKAGE_TARGETS']:
            with tools.environment_append(RunEnvironment(self).vars):
                bin_path = os.path.join(variant, "bin", "test_package")
                if self.settings.os == "Windows":
                    self.run(bin_path)
                elif self.settings.os == "Macos":
                    self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path))
                else:
                    self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path))
