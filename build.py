#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default, build_shared


def add_build_requires(builds):
    return map(add_required_installers, builds)


def add_required_installers(build):
    installers = ['nasm_installer/2.13.02@bincrafters/stable']
    if build_shared.get_os() == "Windows":
        installers.append('msys2_installer/laster@bincrafters/stable')
    build.build_requires.update({"*": installers})
    return build


if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=False)

    builder.items = add_build_requires(builder.items)

    builder.run()
