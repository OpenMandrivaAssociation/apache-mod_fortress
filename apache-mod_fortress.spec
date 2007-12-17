#Module-Specific definitions
%define mod_name mod_fortress
%define mod_conf 81_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Mod_fortress is a DSO module for the apache Web server
Name:		apache-%{mod_name}
Version:	1.0
Release:	%mkrel 5
Group:		System/Servers
License:	GPL
URL:		http://www.spunge.org/~io/fortress.html
Source0:	%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Source2:	mod_fortress_signatures.conf.bz2
Patch0:		fortress-gcc4.patch
Patch1:		mod_fortress-1.0-apache220.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  apache-conf >= 2.2.0
Requires(pre):  apache >= 2.2.0
Requires:       apache-conf >= 2.2.0
Requires:       apache >= 2.2.0
BuildRequires:  apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1

%description
mod_fortress is an HTTP application firewall and intrusion
detection system, it relies on analysing requests sent from the
client to the webserver, and logs specific malicious requests with
extensive info about the attacker as well as the attacked server 
(if multiple virtual servers). It also has the ability to act as a
non-transparent proxy, thus, protecting/obscuring your server via
sending false return HTTP error codes.

%prep

%setup -q -n fortress
%patch0 -p0

#Fix symbol conflict between mod_fortress and mod_smbauth
#Programmers lack imagination when creating function names!
perl -pi -e "s/strupper/fort_strupper/g;" mod_fortress.c

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%patch1 -p1

%build

%{_sbindir}/apxs -c %{mod_name}.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_sysconfdir}/httpd/conf

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

bzcat %{SOURCE2} > %{buildroot}%{_sysconfdir}/httpd/conf/mod_fortress_signatures.conf

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/mod_fortress_signatures.conf
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*


