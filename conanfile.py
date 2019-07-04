#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import fnmatch


class OpenH264Conan(ConanFile):
    name = "openh264"
    version = "1.7.0"
    url = "https://github.com/bincrafters/conan-openh264"
    author = "Bincrafters <bincrafters@gmail.com>"
    homepage = 'http://www.openh264.org/'
    description = "Open Source H.264 Codec"
    topics = ("conan", "h264", "codec", "video", "compression", )
    license = "BSD-2-Clause"
    exports = ["LICENSE.md"]

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {'shared': 'False'}
    _source_subfolder = "sources"

    def build_requirements(self):
        self.build_requires("nasm_installer/2.13.02@bincrafters/stable")

    def source(self):
        source_url = "https://github.com/cisco/openh264"
        url = "{0}/archive/v{1}.tar.gz".format(source_url, self.version)
        tools.get(url, sha256="9c07c38d7de00046c9c52b12c76a2af7648b70d05bd5460c8b67f6895738653f")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
        with tools.chdir(self._source_subfolder):
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
                tools.replace_in_file(os.path.join('build', 'platform-msvc.mk'),
                                      'CFLAGS_OPT += -MT',
                                      'CFLAGS_OPT += -%s' % str(self.settings.compiler.runtime))
                tools.replace_in_file(os.path.join('build', 'platform-msvc.mk'),
                                      'CFLAGS_DEBUG += -MTd -Gm',
                                      'CFLAGS_DEBUG += -%s -Gm' % str(self.settings.compiler.runtime))
                args.append('OS=msvc')
                env_build.flags.append('-FS')
            elif self.settings.compiler == 'clang' and self.settings.compiler.libcxx == 'libc++':
                tools.replace_in_file('Makefile', 'STATIC_LDFLAGS=-lstdc++', 'STATIC_LDFLAGS=-lc++\nLDFLAGS+=-lc++')
            env_build.make(args=args)
            args.append('install')
            env_build.make(args=args)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.options.shared:
            exts = ['*.a']
        else:
            exts = ['*.dll', '*.so*', '*.dylib*']
        for root, _, filenames in os.walk(self.package_folder):
            for ext in exts:
                for filename in fnmatch.filter(filenames, ext):
                    os.unlink(os.path.join(root, filename))

    def package_info(self):
        if self.settings.compiler == 'Visual Studio' and self.options.shared:
            self.cpp_info.libs = ['openh264_dll']
        else:
            self.cpp_info.libs = ['openh264']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append('pthread')
