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

    def source(self):
        source_url = "https://github.com/cisco/openh264"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            msys_bin = self.deps_env_info['msys2_installer'].MSYS_BIN
            with tools.environment_append({'PATH': [msys_bin],
                                           'CONAN_BASH_PATH': os.path.join(msys_bin, 'bash.exe')}):
                with tools.vcvars(self.settings, filter_known_paths=False, force=True):
                    self.build_configure()
        else:
            self.build_configure()

    def build_configure(self):
        with tools.chdir(self.source_subfolder):
            prefix = os.path.abspath(self.package_folder)
            if self.settings.compiler == 'Visual Studio':
                prefix = tools.unix_path(prefix, tools.MSYS2)
            tools.replace_in_file('Makefile', 'PREFIX=/usr/local', 'PREFIX=%s' % prefix)
            if self.settings.arch == 'x86':
                arch = 'i386'
            elif self.settings.arch == 'x86_64':
                arch = 'x86_64'
            args = ['ARCH=%s' % arch]

            env_build = AutoToolsBuildEnvironment(self)
            if self.settings.compiler == 'Visual Studio':
                args.append('OS=msvc')
                env_build.flags.append('-FS')
            env_build.make(args=args)
            args.append('install')
            env_build.make(args=args)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)

    def package_info(self):
        if self.settings.compiler == 'Visual Studio' and self.options.shared:
            self.cpp_info.libs = ['openh264_dll']
        else:
            self.cpp_info.libs = ['openh264']
