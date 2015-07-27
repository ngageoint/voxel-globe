%include %{_sourcedir}/common.inc

Name:		celery
Version:	3.1.18
Release:	1%{?dist}
Summary:	Distributed Task Queue for Python
Source:		%{name}-%{version}.tar.gz
Source1:        common.inc

License:	New BSD
Group:		Development/Languages
URL: 		http://pypi.python.org/pypi/%{name}
BuildRoot: 	%{_tmppath}/%{name}-%{version}-root
BuildRequires:  python-devel
Requires:       python, setuptools
BuildArch: 	noarch

%description
Task queues are used as a mechanism to distribute work across threads or machines.

A task queue's input is a unit of work, called a task, dedicated worker processes then constantly monitor the queue for new work to perform.

Celery communicates via messages, usually using a broker to mediate between clients and workers. To initiate a task a client puts a message on the queue, the broker then delivers the message to a worker.

A Celery system can consist of multiple workers and brokers, giving way to high availability and horizontal scaling.

Celery is a library written in Python, but the protocol can be implemented in any language. So far there's RCelery for the Ruby programming language, and a PHP client, but language interoperability can also be achieved by using webhooks.

%prep
%setup -q -n %{name}-%{version}

%build
env CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --prefix=${RPM_BUILD_ROOT}%{cat_prefix} --install-data=${RPM_BUILD_ROOT}%{_datadir} --single-version-externally-managed --record=/dev/null

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/

