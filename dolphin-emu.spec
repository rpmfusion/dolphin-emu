Name:           dolphin-emu
Version:        4.0
Release:        6%{?dist}
Summary:        Gamecube / Wii / Triforce Emulator

Url:            http://dolphin-emu.org/
License:        GPLv2 and BSD and Public Domain
#Download here: https://dolphin-emu.googlecode.com/archive/4.0.2.zip
Source0:        %{name}-2879cbd2b564.zip
#Manpage from Ubuntu package
Source1:        %{name}.1
#Kudos to Richard on this one (allows for shared clrun lib):
Patch0:         %{name}-%{version}-clrun.patch
#Kudos to Hans de Goede (updates paths for compat-SFML16-devel):
Patch1:         %{name}-%{version}-compat-SFML16.patch
#GTK3 patch, bug: https://code.google.com/p/dolphin-emu/issues/detail?id=7069
Patch2:         %{name}-%{version}-gtk3.patch
#Use polarssl 1.3, workaround for fedora bug:
#https://bugzilla.redhat.com/show_bug.cgi?id=1069394
#Also see rpmfusion bug for details:
#https://bugzilla.rpmfusion.org/show_bug.cgi?id=2995
Patch3:         %{name}-%{version}-polarssl13.patch
#GCC 4.9, mostly fixed upstream, see bug for an include issue:
#
Patch4:         %{name}-%{version}-gcc49.patch

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
BuildRequires:  SDL2-devel
BuildRequires:  wxGTK3-devel
BuildRequires:  gtk3-devel
BuildRequires:  zlib-devel
BuildRequires:  scons
BuildRequires:  compat-SFML16-devel
BuildRequires:  SOIL-devel
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  bochs-devel
BuildRequires:  opencl-utils-devel
BuildRequires:  soundtouch-devel
BuildRequires:  polarssl-devel >= 1.3.0
BuildRequires:  miniupnpc-devel
BuildRequires:  libusb-devel

Requires:       hicolor-icon-theme

%description
#taken from here: http://code.google.com/p/dolphin-emu/
Dolphin is a Gamecube, Wii and Triforce (the arcade machine based on the
Gamecube) emulator which supports many extra features and abilities not 
present on the original consoles.

%prep
%setup -q -n %{name}-2879cbd2b564
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

###CMAKE fixes
#Allow building with cmake macro
sed -i '/CMAKE_C.*_FLAGS/d' CMakeLists.txt
#This is a typo: https://code.google.com/p/dolphin-emu/issues/detail?id=7074
sed -i 's/soundtouch.h/SoundTouch.h/g' CMakeLists.txt

###Remove all Bundled Libraries except Bochs:
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
%cmake \
       -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DBUILD_SHARED_LIBS=FALSE \
       -DENCODE_FRAMEDUMPS=FALSE \
       -DUSE_EXTERNAL_CLRUN=TRUE \
       -DCLRUN_INCLUDE_PATH=%{_includedir}/opencl-utils/include \
       -DwxWidgets_CONFIG_EXECUTABLE=%{_libexecdir}/wxGTK3/wx-config \
       .

make %{?_smp_mflags}

%install
make %{?_smp_mflags} install DESTDIR=%{buildroot}

desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

#Install manpage:
install -p -D -m 0644 %{SOURCE1} \
    %{buildroot}/%{_mandir}/man1/%{name}.1

%find_lang %{name}

%files -f %{name}.lang
%doc license.txt Readme.txt docs/*
%doc docs/ActionReplay/GCNCodeTypes.txt
%{_datadir}/%{name}
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_mandir}/man1/%{name}.*
%{_datadir}/pixmaps/%{name}.xpm

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
* Tue Dec 9 2014 Jeremy Newton <alexjnewt@hotmail.com> - 4.0-6
- Patching for GCC 4.9
- GTK patch fixing

* Sat Dec 6 2014 Jeremy Newton <alexjnewt@hotmail.com> - 4.0-5
- Line got deleted by accident, build fails

* Mon Oct 27 2014 Jeremy Newton <alexjnewt@hotmail.com> - 4.0-4
- Change in wxGTK3-devel file
- Remove unnecessary CG requirement

* Thu Oct 2 2014 Jeremy Newton <alexjnewt@hotmail.com> - 4.0-3
- Use polarssl 1.3 (fedora 21+) to avoid bundling
- patch to use entropy functionality in SSL instead of havege

* Thu Oct 2 2014 Jeremy Newton <alexjnewt@hotmail.com> - 4.0-2
- Bundle polarssl (temporary fix, only for F19/20)

* Mon Mar 3 2014 Jeremy Newton <alexjnewt@hotmail.com> - 4.0-1
- Update to dolphin 4.0.2
- Removed any unnecessary patches
- Added new and updated some old patches
- Removed exclusive arch, now builds on arm

* Wed Jan 1 2014 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-6
- Build for SDL2 (Adds vibration support)

* Mon Nov 18 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-5
- Added patch for SFML, thanks to Hans de Goede

* Sat Jul 27 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-4
- Updated for SFML compat

* Fri Jul 26 2013 Jeremy Newton <alexjnewt@hotmail.com> - 3.5-3
-3 GCC 4.8 Fix (Fedora 19 and onwards)

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
