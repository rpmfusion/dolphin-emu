Name:           dolphin-emu
Version:        3.5
Release:        6%{?dist}
Summary:        Gamecube / Wii / Triforce Emulator

Url:            http://www.dolphin-emulator.com/
#A license breakdown is included in copyright from Source1
License:        GPLv2 and BSD and OpenSSL and Public Domain
##Source can be grabbed using the script in Source1:
#get-source-from-git.sh
Source0:        %{name}-%{version}.tar.xz
#Source1 just contains various missing files from the source
#Most of it can be grabbed here:
#https://github.com/chenxiaolong/Fedora-SRPMS/tree/master/dolphin-emu
#The copyright file is from here:
#http://ppa.launchpad.net/glennric/dolphin-emu/ubuntu/pool/main/d/dolphin-emu/dolphin-emu_3.0-0ubuntu2~lucid.debian.tar.gz
Source1:        %{name}-extra.tar.xz
#Kudos to Richard on this one (allows for shared clrun lib):
Patch0:         %{name}-%{version}-clrun.patch
#Allows for building with wxwidget 2.8.12, rather than 2.9.3
Patch1:         %{name}-%{version}-wx28.patch
#Kudos to Hans de Goede (updates paths for compat-SFML16-devel):
Patch2:         %{name}-%{version}-compat-SFML16.patch

# Dolphin only runs on Intel x86 archictures
ExclusiveArch:  i686 x86_64

BuildRequires:  alsa-lib-devel
BuildRequires:  bluez-libs-devel
BuildRequires:  cmake
BuildRequires:  cairo-devel
BuildRequires:  glew-devel
BuildRequires:  libao-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libXrandr-devel
BuildRequires:  lzo-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  openal-soft-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  portaudio-devel
BuildRequires:  SDL-devel
BuildRequires:  wxGTK-devel
BuildRequires:  zlib-devel
BuildRequires:  Cg
BuildRequires:  scons
BuildRequires:  compat-SFML16-devel
BuildRequires:  SOIL-devel
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  bochs-devel
BuildRequires:  opencl-utils-devel
Requires:       hicolor-icon-theme

%description
#taken from here: http://code.google.com/p/dolphin-emu/
Dolphin is a Gamecube, Wii and Triforce (the arcade machine based on the
Gamecube) emulator which supports many extra features and abilities not 
present on the original consoles.

%prep
%setup -q -a 1
%patch0 -p1
%patch1 -p1
%patch2 -p1

#Patch for GCC 4.8
sed -i 's/_rot/__rot/g' Externals/Bochs_disasm/PowerPCDisasm.cpp Externals/wxWidgets3/include/wx/image.h Externals/wxWidgets3/src/generic/graphicc.cpp Externals/wxWidgets3/src/common/cairo.cpp Externals/wxWidgets3/src/common/image.cpp Externals/wxWidgets3/src/gtk/gnome/gprint.cpp Externals/wxWidgets3/src/gtk/dcclient.cpp Externals/wxWidgets3/src/gtk/print.cpp Source/Core/Core/Src/PowerPC/Jit64/Jit_Integer.cpp Source/Core/Core/Src/PowerPC/Jit64IL/IR.cpp Source/Core/Core/Src/PowerPC/Interpreter/Interpreter_Integer.cpp Source/Core/Core/Src/ARDecrypt.cpp Source/Core/Common/Src/CommonFuncs.h Source/Core/Common/Src/Hash.cpp
#Various CMAKE fixes
sed -i '/CMAKE_C.*_FLAGS/d' CMakeLists.txt
sed -i 's/ AND NOT SFML_VERSION_MAJOR//g' CMakeLists.txt

#Remove all Bundled Libraries except Bochs:
cd Externals
rm -f -r `ls | grep -v 'Bochs_disasm'`
#Remove Bundled Bochs source and replace with links:
cd Bochs_disasm
rm -f -r `ls | grep -v 'PowerPC*' | grep -v 'CMakeLists.txt'`
mv PowerPCDisasm.cpp PowerPCDisasm.cc
sed -i 's/cpp/cc/' CMakeLists.txt
ln -s /usr/include/bochs/config.h ./config.h
ln -s /usr/include/bochs/disasm/*.cc ./
ln -s /usr/include/bochs/disasm/*.inc ./
ln -s /usr/include/bochs/disasm/*.h ./

%build
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DBUILD_SHARED_LIBS=FALSE \
       -DENCODE_FRAMEDUMPS=FALSE \
       -DUSE_EXTERNAL_CLRUN=TRUE \
       -DCLRUN_INCLUDE_PATH=%{_includedir}/opencl-utils/include \
       .
make %{?_smp_mflags}

%install
make %{?_smp_mflags} install DESTDIR=%{buildroot}

#Install extras from source1:
for size in 16 32 48 128 256; do
    dim="${size}x${size}"
    install -p -D -m 0644 %{name}-extra/%{name}$size.png \
    %{buildroot}%{_datadir}/icons/hicolor/$dim/apps/%{name}.png
done
desktop-file-install --dir %{buildroot}%{_datadir}/applications \
    %{name}-extra/%{name}.desktop
install -p -D -m 0644  %{name}-extra/%{name}.1 \
    %{buildroot}/%{_mandir}/man1/%{name}.1
%find_lang %{name}

%files -f %{name}.lang
%doc license.txt Readme.txt docs/ActionReplay/CodeTypesGuide.txt
%doc docs/ActionReplay/GCNCodeTypes.txt %{name}-extra/copyright
%{_datadir}/%{name}
%{_bindir}/%{name}
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_mandir}/man1/%{name}.*

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Mon Sep 01 2014 Sérgio Basto <sergio@serjux.com> - 3.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Nov 18 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-5
- Added patch for SFML, thanks to Hans de Goede

* Sat Jul 27 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-4
- Updated for SFML 2.0 update

* Fri Jul 26 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-3
- GCC 4.8 Fix (Fedora 19 and onwards)

* Tue Feb 19 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-2
- Fixed date typos in SPEC

* Tue Feb 19 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-1
- Updated to latest stable: removed GCC patch, updated CLRun patch
- Added patch to build on wxwidgets 2.8 (temporary workaround)

* Sat Feb 16 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-12
- Removed patch for libav and disabled ffmpeg, caused rendering issues
- Minor consistency fixes to SPEC file

* Fri Dec 14 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-11
- Added patch for recent libav api change in fc18, credit to Xiao-Long Chen
- Renamed patch 1 for consistency

* Mon Jun 25 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-10
- Changed CLRun buildrequire package name
- Renamed GCC 4.7 patch to suit fedora standards
- Added missing hicolor-icon-theme require

* Sat Jun 02 2012 Xiao-Long Chen <chenxiaolong@cxl.epac.to> - 3.0-9
- Add patch to fix build with gcc 4.7.0 in fc17

* Thu Apr 5 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-8
- Removed bundled CLRun

* Tue Mar 13 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-7
- Removed bundled bochs
- Fixed get-source-from-git.sh: missing checkout 3.0

* Fri Feb 24 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-6
- Removed purposeless zerolength file
Lots of clean up and additions, thanks to Xiao-Long Chen:
- Added man page
- Added script to grab source
- Added copyright file
- Added ExclusiveArch
- Added Some missing dependencies

* Thu Feb 23 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-5
- Fixed Licensing
- Split sources and fixed source grab commands

* Fri Jan 27 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-4
- Tweaked to now be able to encode frame dumps

* Sun Jan 22 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-3
- Building now uses cmake macro
- Turned off building shared libs
- Removed unnecessary lines
- Fixed debuginfo-without-sources issue
- Reorganization of the SPEC for readability

* Thu Jan 12 2012 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-2
- Fixed up spec to Fedora Guidelines
- Fixed various trivial mistakes
- Added SOIL and SFML to dependancies
- Removed bundled SOIL and SFML from source spin

* Sun Dec 18 2011 Jeremy Newton <alexjnewt@hotmail.com> - 3.0-1
- Initial package SPEC created
