# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}
%define jafver  1.0.2

Name:           classpathx-jaf
Version:        1.0
Release:        15.4%{?dist}
Epoch:          0
Summary:        GNU JavaBeans(tm) Activation Framework
Group:          System Environment/Libraries
License:        GPLv2+
URL:            http://www.gnu.org/software/classpathx/
Source0:        http://ftp.gnu.org/gnu/classpathx/activation-1.0.tar.gz
Source1:        http://ftp.gnu.org/gnu/classpathx/activation-1.0.tar.gz.sig
Patch0:         classpathx-jaf-MimeType.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires(preun): %{_sbindir}/update-alternatives
Requires(post): %{_sbindir}/update-alternatives
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  java-devel
Provides:       jaf = 0:%{jafver}
Obsoletes:      gnujaf <= 0:1.0-0.rc1.1jpp

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
Requires(post):         java-gcj-compat
Requires(postun):       java-gcj-compat
%else
BuildArch:      noarch
%endif

%description
JAF provides a means to type data and locate components suitable for
performing various kinds of action on it. It extends the UNIX standard
mime.types and mailcap mechanisms for Java.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Provides:       jaf-javadoc = 0:%{jafver}
Obsoletes:      gnujaf-javadoc <= 0:1.0-0.rc1.1jpp
Requires(preun): %{_sbindir}/update-alternatives
Requires(post): %{_sbindir}/update-alternatives
BuildRequires:  java-javadoc

%description    javadoc
%{summary}.

%prep
%setup -q -n activation-%{version}

%patch0 -p0

%build
export JAVAC=%{javac}
export JAR=%{jar}
export JAVADOC=%{javadoc}
%configure
%{__make}
%{__make} javadoc JAVADOCFLAGS="-link %{_javadocdir}/java"


%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
cd $RPM_BUILD_ROOT%{_javadir}
mv activation.jar %{name}-%{version}.jar
ln -s %{name}-%{version}.jar %{name}.jar
ln -s %{name}.jar jaf.jar
#ln -s %{name}-%{version}.jar jaf-%{jafver}.jar
ln -s %{name}-%{version}.jar activation.jar
cd -
install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pR docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}
# for %%ghost
ln -s %{name} $RPM_BUILD_ROOT%{_javadocdir}/jaf 
ln -s %{name} $RPM_BUILD_ROOT%{_javadocdir}/activation

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- classpathx-jaf <= 0:1.0-7jpp_5fc
# Remove file from old non-free packages
%{__rm} -f %{_javadir}/jaf.jar
# Recreate the link as update-alternatives could not do it
%{__ln_s} %{_sysconfdir}/alternatives/jaf %{_javadir}/jaf.jar

%post
%{_sbindir}/update-alternatives --install %{_javadir}/jaf.jar jaf %{_javadir}/%{name}.jar 10002
%{_sbindir}/update-alternatives --install %{_javadir}/activation.jar activation %{_javadir}/%{name}.jar 10002

%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%post javadoc
%{_sbindir}/update-alternatives --install %{_javadocdir}/jaf jaf_javadoc %{_javadocdir}/%{name} 10002
%{_sbindir}/update-alternatives --install %{_javadocdir}/activation activation_javadoc %{_javadocdir}/%{name} 10002

%if %{gcj_support}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%preun
if [ "$1" = "0" ]; then
    %{_sbindir}/update-alternatives --remove jaf %{_javadir}/%{name}.jar
    %{_sbindir}/update-alternatives --remove activation %{_javadir}/%{name}.jar
fi

%preun javadoc
if [ "$1" = "0" ]; then
    %{_sbindir}/update-alternatives --remove jaf_javadoc %{_javadocdir}/%{name}
    %{_sbindir}/update-alternatives --remove activation_javadoc %{_javadocdir}/%{name}
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog COPYING
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%ghost %{_javadir}/activation.jar
%ghost %{_javadir}/jaf.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/classpathx-jaf-1.0.jar.*
%endif

%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{name}
%{_javadocdir}/%{name}-%{version}
%ghost %{_javadocdir}/jaf
%ghost %{_javadocdir}/activation

%changelog
* Mon Feb 08 2010 Jeff Johnston <jjohnstn@redhat.com> - 0:1.0-15.4
- Resolves: #562407
- Make separate alternatives for main package and javadoc sub-package

* Tue Feb 02 2010 Jeff Johnston <jjohnstn@redhat.com> - 0:1.0-15.3
- Fix rpmlint warnings

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0:1.0-15.2
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.0-15.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.0-14.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 23 2008 David Walluck <dwalluck@redhat.com> 0:1.0-13.1
- add %%{_javadir}/jaf.jar as %%ghost
- add %%{_javadir}/activation.jar as alternative
- remove jaf-%%{jafver}.jar link
- own %%{_libdir}/gcj/%%{name}
- add generic javadoc directories as alternatives

* Sun Sep 21 2008 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-13
- Fix Patch0:/%%patch mismatch.

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.0-12
- drop repotag
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.0-11jpp.1
- Autorebuild for GCC 4.3

* Sun Mar 11 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.0-10jpp.1.fc7
- Resync with latest from JPP

* Fri Aug 18 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.0-9jpp.1
- Resync with latest from JPP.

* Fri Aug 11 2006 Vivek Lakshmanan <vivekl@redhat.com> - 0:1.0-8jpp.1
- Replace explicit Requires(post) on coreutils with 
  Requires-post/postun on rm and ln since more portable with JPP.
- Revert explicit install of versionless jaf.jar install since
  alternatives handles this.
- Extend triggerpostun to trigger on <= 0:1.0-7jpp_5fc so jaf.jar
  exists when upgrading from -7jpp_5fc.

* Thu Aug 10 2006 Karsten Hopp <karsten@redhat.de> 1.0-7jpp_5fc
- Requires(post):     coreutils

* Sun Jul 23 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.0-7jpp_4fc
- Install versionless jaf.jar symlink.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> 0:1.0-7jpp_3fc
- Rebuilt

* Thu Jul 20 2006 Vivek Lakshmanan <vivekl@redhat.com> 0:1.0-7jpp_2fc
- Rebuild.

* Tue Jul 18 2006 Vivek Lakshmanan <vivekl@redhat.com> 0:1.0-7jpp_1fc
- Add conditional native compilation with GCJ.
- Merge with latest from JPP.

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - sh: line 0: fg: no job control
- rebuild

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:1.0-2jpp_5fc
- stop scriptlet spew

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> 0:1.0-2jpp_4fc
- rebuilt

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Jan 11 2005 Gary Benson <gbenson@redhat.com> 0:1.0-2jpp_3fc
- Sync with RHAPS.

* Mon Nov  1 2004 Gary Benson <gbenson@redhat.com> 0:1.0-2jpp_2fc
- Build into Fedora.

* Thu Oct 28 2004 Fernando Nasser <fnasser@redhat.com> 0:1.0-2jpp_1rh
- First Red Hat build

* Fri Aug 20 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.0-2jpp
- Pro forma rebuild with ant-1.6.2 present

* Tue Jun 15 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-1jpp
- Update to 1.0.

* Fri Jun 11 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-0.rc1.2jpp
- Bump release to work around bug in rpm <https://bugzilla.redhat.com/116299>.

* Thu Jun 10 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-0.rc1.1jpp
- Rename gnujaf to classpathx-jaf.

* Fri May 28 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-0.rc1.1jpp
- First build.
