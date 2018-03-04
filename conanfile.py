#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class OpenH264Conan(ConanFile):
    name = "openh264"
    version = "1.7.0"
    url = "https://github.com/bincrafters/conan-openh264"
    homepage = 'http://www.openh264.org/'
    description = "Open Source H.264 Codec"
    license = "BSD 2-Clause"
    exports = ["LICENSE.md"]

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    source_subfolder = "sources"

    def build_requirements(self):
        self.build_requires('nasm_installer/[>=2.13.02]@bincrafters/stable')

    def source(self):
        source_url = "https://github.com/cisco/openh264"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            prefix = os.path.abspath(self.package_folder)
            tools.replace_in_file('Makefile', 'PREFIX=/usr/local', 'PREFIX=%s' % prefix)
            if self.settings.arch == 'x86':
                arch = 'i386'
            elif self.settings.arch == 'x86_64':
                arch = 'x86_64'
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make(args=['ARCH=%s' % arch])
            env_build.make(args=['install'])

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
